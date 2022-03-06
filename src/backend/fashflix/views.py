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
from .ml.recommender import KNearestRecommender
from .ml.utils import make_embedding_callback


class Config:
    NUM_LABELS = 13
    WEIGHTS_PATH = os.path.join(settings.BASE_DIR, "fashflix/ml/2022-02-08_23-53-14/best_model.pt")
    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
    VOTES_DF_PATH = "votes.csv"


class ML:
    SETUP_DONE = False
    preference_vector = None

    @classmethod
    def setup(cls):
        if cls.SETUP_DONE: return True

        database = FashionDatabase()
        print(f"Metadata Database: {database.metadata_database.read_df().count()}")
        print(f"Embeddings Database: {database.embeddings_database.read_df().count()}")

        recommender = KNearestRecommender()
        embeddings_df = database.embeddings_database.read_df()
        embeddings_pdf = embeddings_df.toPandas()
        embeddings_pdf["embeddings"] = embeddings_pdf.embeddings_json.apply(lambda embedding_json: np.array(json.loads(embedding_json), dtype="float"))
        embeddings_data = np.array(embeddings_pdf["embeddings"].values.tolist())
        recommender.fit(embeddings_data)

        model = ResnetDummy(Config.NUM_LABELS, freeze_pretrain=False)
        model.load_state_dict(torch.load(Config.WEIGHTS_PATH, map_location=torch.device(Config.DEVICE)))
        model = model.to(Config.DEVICE)
        model.eval()
        transforms = get_data_transforms()["test"]

        def get_img_embedding(img):
            img = transforms(img).unsqueeze(0).to(Config.DEVICE)
            embedding = model.embed(img).cpu().detach().numpy().flatten()
            return embedding

        embedding_callback = make_embedding_callback(get_img_embedding)

        def model_callback(preference_vector):
            if cls.preference_vector is None:
                if preference_vector is None:
                    cls.preference_vector = embeddings_data.mean(axis=0).reshape(1, -1)
                else:
                    cls.preference_vector = preference_vector

            recommendation_uuids = recommender.get_recommendations(preference_vector, embeddings_pdf)
            recommendation_uuids = recommendation_uuids[0]
            votes_df = pd.DataFrame({"recommendation_uuid": recommendation_uuids})
            votes_df.to_csv(Config.VOTES_DF_PATH, index=False)
            recommendations = database.get_images_and_metadata(recommendation_uuids)
            return list(recommendations.values())

        cls.model_callback = model_callback
        cls.SETUP_DONE = True
        return True

    @classmethod
    def get_recommendations_from_image(cls, image_url):
        if not cls.SETUP_DONE:
            ML.setup()
        input_image = InputImage(image_url, "input_image")
        input_embeddings = embedding_callback([input_image])
        input_embedding = [input_embeddings[0]] # work on single image
        return cls.model_callback(input_embedding)

    @classmethod
    def get_user_vector(cls, user_id):
        if not cls.SETUP_DONE:
            ML.setup()
        return cls.preference_vector

    @classmethod
    def get_recommendations_for_user(cls, user_id):
        if not cls.SETUP_DONE:
            ML.setup()
        user_vector = cls.get_user_vector(user_id)
        return cls.model_callback(user_vector)


@api_view(["POST"])
def setup(request):
    ML.setup()
    return Response("Setup already done", status=status.HTTP_200_OK)


@api_view(["POST"])
def get_recommendations(request):
    image_url = get_param(request, "imageUrl")
    if image_url:
        recommendations = ML.get_recommendations_from_image(image_url)
        return Response(recommendations, status=status.HTTP_200_OK)

    user = request.user
    print("user:", request.user.id, request.user.username)
    recommendations = ML.get_recommendations_for_user(user.id)
    return Response(recommendations, status=status.HTTP_200_OK)
    return Response("No input image url in request.", status=status.HTTP_400_BAD_REQUEST)


# ========================================================
#                   USER AUTHENTICATION
# ========================================================


@api_view(["POST"])
def login(request):
    username = get_param(request, "username", None)
    password = get_param(request, "password", None)
    if (username is not None) and (password is not None):
        user = authenticate(username=username, password=password)
        if user is not None:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({"validated": True, "id": user.id, "token": token.key})
    return Response({"validated": False, "code": 0, "message": "Could not validate"})


@api_view(["POST"])
def sign_up(request):
    first_name = get_param(request, "firstname", "")
    last_name = get_param(request, "lastname", "")
    email = get_param(request, "email", None)
    password = get_param(request, "password", None)
    guest_id = get_param(request, "guest_id", None)

    try:
        user = User.objects.get(username=email)
        if user is not None:
            return Response(
                {"validated": False, "code": 1, "message": "User already exists"}
            )
    except User.DoesNotExist:
        pass
    except Exception:
        print(f"Could not retrieve user with email {email}")
        return Response(
            {"validated": False, "code": 2, "message": "Could not create user"}
        )

    try:
        user = User.return_if_guest(guest_id)
        if user is None:
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                is_guest_account=False,
            )
        else:
            user.username = email
            user.email = email
            user.set_password(password)
            user.first_name = first_name
            user.last_name = last_name
            user.is_guest_account = False
        user.save()
        return Response({"validated": True, "id": user.id})
    except Exception:
        print(f"Could not create user with email {email}")
        return Response(
            {"validated": False, "code": 0, "message": "Invalid account details"}
        )


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
