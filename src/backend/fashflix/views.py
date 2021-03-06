from django.conf import settings
from rest_framework import status, viewsets
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
# from lazysignup.decorators import allow_lazy_user

# from .serializers import OutputImageSerializer
from .models import User

import json
import os
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st
import torch

from .common.auth_utils import get_random_string
from .common.django_utils import get_param
from .common.file_utils import read_df
from .common.image_utils import InputImage
from .data.database import FashionDatabase
from .ml.dataloader import load_datasets, get_data_transforms
from .ml.dummy import Identity, Rotate
from .ml.model import ResnetDummy
from .ml.recommender import KNearestRecommender, NoopPreferenceOptimizer, WeightedPreferenceOptimizer
from .ml.utils import make_embedding_callback


class Config:
    NUM_LABELS = 13
    WEIGHTS_PATH = os.path.join(settings.BASE_DIR, "fashflix/ml/2022-02-08_23-53-14/best_model.pt")
    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
    VOTES_DF_PATH = "votes.csv"

    NUM_RECOMMENDATIONS = 200
    NUM_USER_RECOMMENDATIONS = 20
    NUM_IMAGE_RECOMMENDATIONS = 10

    OPTIMIZER = WeightedPreferenceOptimizer


class ML:
    SETUP_DONE = False
    preference_vector = None

    @classmethod
    def setup(cls):
        if cls.SETUP_DONE: return True

        cls.database = FashionDatabase()
        print(f"Metadata Database: {cls.database.metadata_database.read_df().count()}")
        print(f"Embeddings Database: {cls.database.embeddings_database.read_df().count()}")

        recommender = KNearestRecommender(n_neighbors=Config.NUM_RECOMMENDATIONS)
        embeddings_df = cls.database.embeddings_database.read_df()
        embeddings_pdf = embeddings_df.toPandas()
        embeddings_pdf["embeddings"] = embeddings_pdf.embeddings_json.apply(lambda embedding_json: np.array(json.loads(embedding_json), dtype="float"))
        embeddings_data = np.array(embeddings_pdf["embeddings"].values.tolist())
        cls.default_preference_vector = embeddings_data.mean(axis=0).reshape(1, -1)
        recommender.fit(embeddings_data)

        cls.preference_optimizer = Config.OPTIMIZER()

        model = ResnetDummy(Config.NUM_LABELS, freeze_pretrain=False)
        model.load_state_dict(torch.load(Config.WEIGHTS_PATH, map_location=torch.device(Config.DEVICE)))
        model = model.to(Config.DEVICE)
        model.eval()
        transforms = get_data_transforms()["test"]

        def get_img_embedding(img):
            img = transforms(img).unsqueeze(0).to(Config.DEVICE)
            embedding = model.embed(img).cpu().detach().numpy().flatten()
            return embedding

        cls.embedding_callback = make_embedding_callback(get_img_embedding)

        def model_callback(preference_vector, n_neighbors):
            if preference_vector is None:
                preference_vector = cls.default_preference_vector

            preference_vector = np.array(preference_vector)
            # print("preference_vector shape:", preference_vector.shape)
            recommendation_uuids = recommender.get_recommendations(preference_vector, embeddings_pdf)
            # print("n_neighbors:", n_neighbors)
            recommendation_uuids = recommendation_uuids[:n_neighbors] #recommendation_uuids[0][:n_neighbors]
            votes_df = pd.DataFrame({"recommendation_uuid": recommendation_uuids})
            votes_df.to_csv(Config.VOTES_DF_PATH, index=False)
            recommendations = cls.database.get_images_and_metadata(recommendation_uuids)
            return [{**recc_details, "id": recc_id} for recc_id, recc_details in recommendations.items()]

        cls.model_callback = model_callback
        cls.SETUP_DONE = True
        return True


    @classmethod
    def get_recommendations_from_image(cls, image_url, user_id):
        if not cls.SETUP_DONE:
            ML.setup()
        input_image = InputImage(image_url, "input_image")
        input_embeddings = cls.embedding_callback([input_image])
        input_embedding = [input_embeddings[0]] # work on single image
        return cls.model_callback(input_embedding, Config.NUM_IMAGE_RECOMMENDATIONS)


    @classmethod
    def get_user_vector(cls, user_id):
        if not cls.SETUP_DONE:
            ML.setup()
        try:
            user = User.objects.get(pk=user_id)
            user_vector = json.loads(get_param(user, "preference_vector", "null"))
            if user_vector is None:
                user.preference_vector = json.dumps(cls.default_preference_vector.tolist())
                user_vector = json.loads(user.preference_vector)
                user.save()
            return user_vector
        except Exception as e:
            print(f"Error in getting user vector for id {user_id}: {e}")
            pass
        return cls.default_preference_vector


    @classmethod
    def get_recommendations_for_user(cls, user_id):
        if not cls.SETUP_DONE:
            ML.setup()
        user_vector = cls.get_user_vector(user_id)
        if user_vector is None:
            raise Exception("No vector produced")
        return cls.model_callback(user_vector, Config.NUM_USER_RECOMMENDATIONS)


    @classmethod
    def optimize_preference_vector(cls, votes, image_ids, user_id):
        if not cls.SETUP_DONE:
            ML.setup()
        user = User.objects.get(pk=user_id)
        user_vector = cls.get_user_vector(user_id)
        if user_vector is None:
            raise Exception("User does not have an initialized preference vector")

        image_embeddings = cls.database.get_embeddings(image_ids)
        # print("image_embeddings", image_embeddings)
        updated_vector = cls.preference_optimizer.optimize(
            user_vector[0],
            [image_embeddings[image_id] for image_id in image_ids],
            votes,
        )
        if updated_vector is not None:
            user.preference_vector = json.dumps([updated_vector])
            user.save()
        return updated_vector


@api_view(["POST"])
def setup(request):
    ML.setup()
    return Response("Setup done", status=status.HTTP_200_OK)


@api_view(["POST"])
def get_recommendations(request):
    user = request.user
    # body_unicode = request.body.decode('utf-8')
    # body_data = json.loads(body_unicode)
    # print("request data:", body_data)
    user_id = user.id or get_param(request, "userId")
    image_url = get_param(request, "imageUrl")
    if image_url:
        recommendations = ML.get_recommendations_from_image(image_url, user_id)
        return Response(recommendations, status=status.HTTP_200_OK)

    recommendations = ML.get_recommendations_for_user(user_id)
    return Response(recommendations, status=status.HTTP_200_OK)


@api_view(["POST"])
def ratings(request):
    user_id = request.user.id or get_param(request, "userId")
    image_ids = get_param(request, "imageIds")
    votes = get_param(request, "votes")
    if user_id is not None and image_ids is not None and votes is not None:
        preference_vector = ML.optimize_preference_vector(votes, image_ids, user_id)
        return Response("Updated preferences", status=status.HTTP_200_OK)
    return Response("Incomplete parameters for request", status=status.HTTP_400_BAD_REQUEST)


# ========================================================
#                   USER AUTHENTICATION
# ========================================================


@api_view(["GET"])
def guest_account(request):
    first_name = ""
    last_name = ""
    email = ""
    password = get_random_string(16)

    attempts = 5
    while attempts > 0:
        username = get_random_string(16)
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            break
        attempts -= 1

    try:
        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_guest_account=True,
        )
        user.save()
        return Response({"validated": True, "id": user.id})
    except Exception:
        print(f"Could not create guest user with email {email}")
        return Response(
            {"validated": False, "code": 0, "message": "Could not create account"}
        )


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def authenticate_token(request):
    user = request.user
    username = get_param(request, "username", None)
    if username is None:
        return Response(
            "Invalid request - must provide username to authenticate token.",
            status=status.HTTP_400_BAD_REQUEST,
        )

    if username == user.username:
        return Response({"userId": user.id}, status=status.HTTP_202_ACCEPTED)
    return Response(status=status.HTTP_401_UNAUTHORIZED)
