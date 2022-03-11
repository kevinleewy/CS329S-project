#  FashFlix 🧥
*Team: Manan Rai, Anthony Vento, Kevin Lee*
<br/>

## 1 Problem Definition (200 words)
<!-- * This section explains the problem the team is solving, discusses related work, and proposes and justifies their solution. -->

Consider this: you have been wearing the same outfits for months and decide it is time to spice your wardrobe up.  However, you do not know where to begin since there are so many fashion styles to choose from. You simply do not have the energy nor the time to search through an endless amount of catalogs.  This is where FashFlix comes into play.

With FashFlix, users can save time and effort because we offer quick access to products curated from multiple catalogs, relevant recommendations based on fits you love, and a better, personalized wardrobe in just a few swipes.

Other fashion stores such as Amazon and Macy’s have enormous catalogs that are hard to navigate. Additionally, the right products are obscured by thousands of irrelevant ones. They are dependent on traditional methods of estimating user preference, such as making the user answer a survey (e.g. Stitch Fix), or clicking through desired outfits. 

We want to make the shopping experience as easy as possible, so we draw inspiration from Tinder and Google Lens. The former allows users to specify preferences with a few flicks of the finger, while the latter allows users to use an image to retrieve more images.

## 2 System Design (500 words)

<!-- * This section details the key components of the system, including, but not limited to, data pipelines, modeling, deployment, and UX. 
* If applicable, a diagram is included to illustrate the interplay between system components. Excalidraw is pretty awesome for sketches.
* This section explains and justifies central design decisions, including that of which technologies the team chose to use to support their system. -->

FashFlix is a webapp hosted on the Google Cloud Platform (GCP), with a Django backend and React frontend. Here, we go over the system design, and the key design decisions that led to the final state of the app.

### 2.1 Features
Our system has two core components: giving product recommendations (PR), and refining user preferences (UP). These components are made available to users through three primary features:
- **Exploring Product Recommendations.** Given the current state of a user's preference vector, fetch recommendations from the product catalog and visualize them for the user.
- **Personalizing Recommendations.** Users can give feedback on recommended products using a Tinder-like swiping feature: a left swipe indicates that they did not like a recommendation; a right swipe indicates they did. These swipes are used to update the user's preference vector.
- **Outfit Search.** Given an image of an outfit, the app attempts to recommend similar outfits. This is similar to the first feature, with the primary difference being the vector that the products are queried against: while the former uses the user's preference vector, the latter uses the query image embedding.

### 2.3 Webapp
For the MVP, we leveraged Streamlit to build a locally-hosted full-stack application, along with some custom frontend components designed using React. While Streamlit was effective for a quick proof-of-concept, we found both the frontend to be fairly limited and restrictive. Accordingly, we upgraded to a pure React frontend, with a Django backend. We chose Django over alternate frameworks like Flask because of its easy integration with databases and extended support for user authentication. Accordingly, the system choices we made for the final app allow us more control over what the webapp looks like, alongside a robust and extensible backend.

### Backend
Here, we discuss the key API endpoints exposed by the backend.

**User Sessions and Authentication.** When a user logs onto the app, a temporary guest account is created for them and they are assigned a `userId` that becomes their unique identifier for the application. All subsequent interactions rely on this id, and preference vectors are tied to ids. The backend supports transitioning to authenticated users from these guest accounts, after which requests from the frontend will be tied with authentication tokens that the backend verifies. When the webapp session is recycled (through a browser window close), the `userId` is lost if the user did not log in, but the preference vectors and the user's interactions are not removed from the database.

**Fetching Recommendations.** Given an input embedding, which is either a user preference vector fetched from the database, or an embedding generated for a query image using the embedding model $E$, this endpoint uses the recommender $R$ to find a set of products to recommend. See Section [3.3](#recommender-system) for more details.

**Personalizing Recommendations.** This is an internal-facing endpoint that takes in paired data of image ids and a user's swipes, and passes them to a preference optimizer $O$, which updates the user's preference vector stored in database.

### Frontend

<div style="text-align:center">
    <img src="https://i.imgur.com/Zyz9GF8.png"  alt="system_diagram" width="80%"/>
    <p>Figure 1: System Diagram</p>
</div>

### 2.4 Data Layer

### Product Catalog

**Metadata.** We used Selenium and Beautiful Soup to scrape 4000+ products from online product catalogs like Gap, Express, and Zappos. This gave us access to a large product catalog with metadata inclucing the name, price, rating and number of reviews, product image, original product url, and clothing type (men's or women's) for each product. This acts as our product catalog.

**Embeddings.** We pre-compute the embeddings for the primary image of each product in the catalog. This gives us the embeddings catalog.

### Server-Data Communication

**Apache Spark.** The product and embeddings catalogs are both modeled as Spark dataframes, stored in parquet files, and hosted on GCP. Since Spark is built for big data, this allows easy scaling of the product catalog by allowing us to leverage distirbuted versions of recommendation algorithms.

**MongoDB.** Server-specific data is stored using MongoDB. Currently, this is limited to the user data, including the `userId`s and their prefrence vectors.

### 2.5 Hosting

The app is hosted through GCP. We currently serve both the backend and frontend through separate processes on the same virtual machine in order to limit the amount of GCP credits burned for hosting. Note that the current backend is able to handle cross-origin resource sharing, so hosting the frontend through a static server would be a trivial change.


## 3 Machine Learning Component (400 words)

<!-- * This section explains the ML model(s) that powers the application, the data it’s trained on, and the iterative development of that model. -->

<!-- 487 words -->

At the core of our system is an **embedding model** which returns fashion embeddings for every image, as well as a **recommender system** which returns catalog products based on the fashion embeddings of the query image. We discuss the dataset and models developed.

### 3.1 Dataset
For model training and evaluation, we utilized the  In-Shop Fashion Retrieval Benchmark from the DeepFashion dataset [[1]](#references). This consisted of 52,712 images, each with 463 attributes (buttons, sleeveless, floral, etc) and segmentation masks. Figure 2 illustrates a few samples of images from the dataset. We note that images from this dataset are stock images and not necessarily real life products. 

<div style="text-align:center">
    <img src="https://i.imgur.com/5plOFFF.png"  alt="df_sample_0" width="10%"/>
    <img src="https://i.imgur.com/KviRYtC.png"  alt="df_sample_0" width="10%"/>
    <img src="https://i.imgur.com/1CkKoS5.png"  alt="df_sample_0" width="10%"/>
    <img src="https://i.imgur.com/FsOjWb0.png"  alt="df_sample_0" width="10%"/>
    <img src="https://i.imgur.com/xes5hyv.png"  alt="df_sample_0" width="10%"/>
    <img src="https://i.imgur.com/229k8Yg.png"  alt="df_sample_0" width="10%"/>
    <p>Figure 2: DeepFashion image samples</p>
</div>


<!-- <div style="text-align:center">
    <img src="https://i.imgur.com/Gva6UvW.png"  alt="attr_distr" height="250"/>
    <img src="https://i.imgur.com/Tdd555X.png"  alt="attr_distr" height="250"/>
    <p>Figure 3: DeepFashion image sample with segmentation data</p>
</div> -->


### 3.2 Data Analysis and Preprocessing

#### Classification Attributes

We inspected all attributes and removed duplicate rows, as well as verified that there are no missing data. Upon inspection of each of the 463 attributes, we noticed that there are heavy imbalances across the attributes as shown in Figure 3. 


<div style="text-align:center">
    <img src="https://i.imgur.com/RNAQ9t0.png"  alt="attr_distr" width="75%"/>
    <p>Figure 3: Attribute distribution for samples in train set</p>
</div>

From this observation, we decided to first eliminate 116 attributes that are always "False", leaving 347 attributes. We then narrow down the number of attributes to the top 13 most balanced attributes, which we then increase to 36.

#### Segmentation Data

For the U-Net training described in Section [3.3](#embedding-model), we also converted the labelled segmentation data into binary maps. However, only 6,825 out of 25,882 training samples came with segmentation data.

### 3.3 Methods


### Embedding Model

**Architecture:** We experimented with both ResNet-50 [[2]](#references) and a variation of U-Net [[3]](#references), which we call SegEmbed (See Figure 4), as backbones. The final and bottleneck outputs, respectively, are fed into a fully-connected layer to generate 512-dimensional *fashion embeddings*. The fashion embeddings are then fed into a single-layer classifier for training. At inference, only the ResNet and the encoder-half of SegEmbed are used.

<div style="text-align:center;margin-top:40px">
    <img src="https://i.imgur.com/4upXBON.png" alt="unet_segembed" width="100%" style="margin-bottom:20px"/>
    <p>Figure 4: SegEmbed Model Architecture</p>
</div>


**Training:** We train the ResNet model by optimizing for classification loss. For the U-Net model, we perform a joint optimization for classification and segmentation losses. Due to the imbalance in attributes as mentioned in Section [3.2](#data-analysis-and-preprocessing), the classification loss for each attribute is weighted by the effective number of samples [[4]](#references).

### Recommender System

**Querying:** The recommender system handles queries by finding $K$ nearest neighbors of the input embedding, which could either be a the embedding of a query image or user's preference vector, in fashion embedding space. We selected cosine distance as our distance metric over L2 distance because it [works better for unnormalized vectors](https://datascience.stackexchange.com/questions/27726/when-to-use-cosine-simlarity-over-euclidean-similarity).

**Updating Preferences:** The recommender system updates a user's preference vector, $v_p$ based on a user's recent evaluation on products, such that the new $v_p$ is closer to the embeddings, $e$ of products that the user likes and farther from the ones the user dislikes. The update equation takes the form of an [exponential moving average](https://en.wikipedia.org/wiki/Moving_average#Exponential_moving_average) (EMA), and is shown the equation below.

$$
v_p \leftarrow (1-\alpha) v_p + \alpha \cdot \left(\ \sum_{i\ \in\ \text{liked}}e_i - \sum_{j\ \in\ \text{disliked}}e_j\ \right)
$$

## 4 System Evaluation (500 words)
<!-- 
* This section describes the team’s efforts to validate and evaluate their system performance as well as its limitations.
* The results are included and presented in a clear and informative manner.
 -->
 
<!--  386 words -->
 
### 4.1 Quantitative Evaluation

### Training Evaluation

Table 1 shows the F1-scores for each model during training. **ResNet-50-N** refers to a ResNet-50 model with $N$ classification attributes, where the choice for $N$ is discussed in Section [3.2](#data-analysis-and-preprocessing). (*) denotes that the model was trained with two additional data augmentation steps: color jitter and random rotations.

<div style="text-align:center">
    <img src="https://i.imgur.com/0pZMiux.png"  alt="train_f1" height="130"/>
    <p>Table 1: Validation F1-scores for each model.</p>
</div>

We see that the additional augmentation steps that we performed resulted in lower F-1 scores, but otherwise the ResNet-50 model with 36 attributes achieved the highest F1-score at validation.

### Inference Evaluation
 
We compare the performances of our models by evaluating the quality of the recommendations of each model in the full pipeline (See Section [2](#system-design)). For each selected query image, we generate 10 recommendations from each model, which are then shuffled and presented to human evaluators. These images will then be manually classified as either a "hit" or a "miss" recommendations based on the query image. We perform the evaluation on four of our models (described in Section [3.3](#embedding-model)) as well as on a baseline model that provides recommendations randomly, each on the in-distribution (ID) and out-of-distribution (OOD) catalogs. We also perform the evaluation on three slices of query images: men, women, and mixed.

<div style="text-align:center">
    <img src="https://i.imgur.com/kcQN8Mj.png"  alt="eval_accuracies" height="130"/>
    <p>Table 2: Evaluation Hit Rates (%).</p>
</div>

As shown in Table 2, the OOD hit rates are highest across all query image slices for the ResNet-50 encoder trained on 36 attributes. 

### 4.2 Qualitative Evaluation

We also evaluated our model qualitatively in terms of accuracy and bias. In Figures 5 and 6 below, we see that the model returns images of products that resemble that of the query image. Furthermore, the recommendations are evidently not racially-biased racially towards the query image.

<!-- <div style="text-align:center">
    <img src="https://i.imgur.com/wfN4SqV.png"  alt="eval_bias" width="500"/>
    <p>Figure 5: Qualitative evaluation</p>
</div> -->

<div style="text-align:center">
    <img src="https://i.imgur.com/0Hp39pm.png"  alt="eval_bias" height="200"/>
    <p>Figure 5</p>
</div>

<div style="text-align:center">
    <img src="https://i.imgur.com/niaL5Rd.png"  alt="eval_bias" height="200"/>
    <p>Figure 6</p>
</div>


### 4.3 Limitations

A limitation of our application is that we only train a deep learning model at one moment in time.  However, over time, fashion changes. Therefore, our application will not capture all the "latest and greatest" trends that exist (e.g. brand new products) and could suffer from a distribution shift. Another limitation is simply not capturing all the styles out there since there are so many (e.g. retro, modern, hip, etc.). We are limited to the styles included in the dataset. Our model also performs better on images with simple backgrounds, similar to the dataset distribution. 

## 5 Application Demonstration (200 words)

<!-- * This section includes visuals (screengrab, embedded video link) showcasing the main feature set of the application.
* The section also includes brief justifications of core interface decisions made by the team (e.g. why did the team feel that a Web Application interface would be superior to an API interface given the context of their problem?).
* Instructions on how to use the application. -->

<div style="text-align:center">
    <iframe width="669" height="358"  src="https://youtube.com/embed/yfk0679mbfM" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen=""></iframe>
</div>


## 6 Reflection (500 words)

<!-- * This section provides a comprehensive post-mortem on the project, including - but not limited to - answering the following:
    * What worked? (In terms of technology, design decisions, team dynamics, etc.).
    * What didn’t work? What would you improve next time?
    * If given unlimited time and resources, what would you add to your application?
    * If you have plans to move forward with this application, what are they? (We’re always excited to see how students use the tools they’ve learned in this class to pursue topics they’re excited about!) -->

<!-- 417 words -->

### 6.1 Worked Well
Overall, we are proud of our application. Because our team did a good job of laying out goals for each member each week, we ensured that we completed all aspects of the project and added all the features we desired.

At the beginning of our project, we were worried that it may be very difficult to develop a full machine learning application that 1) looks appealing, 2) is practical, and 3) yields useful results. 

In order to build out an ML application that looks appealing, we first developed a Streamlit UI for our MVP that conveyed relevant  promising recommendations.  After proving that we could build a decent UI, we worked on building an appealing UI in React that showcased our full product.

Additionally, our team was very passionate from day one about building a fashion recommender because of its practicality. Choosing what to wear is arguably as hard as, if not harder than, deciding what to eat. It changes with factors like time, weather and trends, and can further vary depending on a person’s preferences and mood. With our application, it is now feasible and fun (!) to find relevant fashion products. I mean, who does not like the concept of Tinder Swipes for fashion?!

Finally, our approach of iteratively training an embeddings model yielded useful results. This is evident from the results in Section [4.2](#qualitative-evaluation) where the recommender system was able to return relevant products based solely on the embeddings of the query and catalog products.

<div style="text-align:center">
    <img src="https://i.imgur.com/UMHuYpA.png"  alt="eval_bias" width="60%"/>
    <p>Figure 7: Feature we are proud of</p>
</div>

### 6.2 Potential Improvements

Unfortunately, SegEmbed did not perform as well as the ResNet on real world images. We believe this can be improved by either leveraging better pre-trained segmentation models or gathering more labelled, real world samples.


### 6.3 Next Steps
Given unlimited time, there are a variety of things we could do to improve the application and the deployment infrastructure. On the application side, we would allow the user to explicitly filter by type of clothing. For deployment, we would have deployed to a Kubernetes cluster which would help with scaling. We would also have implemented proper CI/CD and written unit and end-to-end test.

In addition, we would work on populating our catalog with more up-to-date products. One option would be to set up a dashboard for vendors to list their products. Another option would be to implement a better and more frequently executed web-scraping infrastructure.

We would also get feedback from users on the current state of FashFlix and incorporate their feedback into our system.

## 7 Broader Impacts (250 words)

<!-- * This section discusses intended uses of your application - and possible unintended uses, and the associated harms.
* This section reflects upon the design decisions that the team undertook to mitigate harms associated with unintended use of the system. -->

<!-- 129 words -->

We expect that users of the application are consumers who are either interested in purchasing clothing, browsing around to see what is available, or trying to keep up with fashion trends.

However, after our MVP, we were worried about only recommending products too expensive (or too cheap) for a user's desired price range. Hence, we included a price filter to allow more users to feel comfortable using our application.

We also included the ratings of the products to help users distinguish good products from bad. However, we still expect users to do their own research into the products, such as by looking at reviews on the vendors' websites. 

Lastly, our application allows equal opportunity to all fashion vendors, including smaller businesses, since the recommender system is agnostic towards branding.


## 8 References

[1] Ziwei Liu, Ping Luo, Shi Qiu, Xiaogang Wang, and Xiaoou Tang. [DeepFashion: Powering robust clothes recognition and retrieval with rich annotations](https://www.cv-foundation.org/openaccess/content_cvpr_2016/papers/Liu_DeepFashion_Powering_Robust_CVPR_2016_paper.pdf). In Proceedings of IEEE Conference on Computer Vision and Pattern Recognition (CVPR), 2016.

[2] Kaiming He, Xiangyu Zhang, Shaoqing Ren, and Jian Sun. [Deep residual learning for image recognition](https://arxiv.org/abs/1512.03385), 2015.

[3] Olaf Ronneberger, Philipp Fischer, and Thomas Brox. [U-Net: Convolutional networks for biomedical image segmentation](https://arxiv.org/abs/1505.04597).
CoRR, abs/1505.04597, 2015.

[4] Yin Cui, Menglin Jia, Tsung-Yi Lin, Yang Song, and Serge J. Belongie. [Class-Balanced Loss Based on Effective Number of Samples](https://arxiv.org/abs/1901.05555). CoRR, abs/1901.05555, 2019.
