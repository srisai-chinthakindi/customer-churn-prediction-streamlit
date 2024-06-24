# importing Modules
import pandas as pd
import numpy as np
from PIL import Image
import base64
import pickle

import streamlit as st

import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Agg')

#load the model from Disk

import joblib
from preprocessing import preprocess

model = joblib.load(r"./notebook/model.sav")



# Setting up the Main Application
def application():
    #Setting Application title
    st.title('Telco Customer Churn Prediction App Designed by KMIT')
    add_bg_from_local("Resources/background2.jpg")

      #Setting Application description
    st.markdown("""
     :dart:  This Streamlit app is made to predict customer churn in a ficitional telecommunication use case.
    The application is functional for both online prediction and batch data prediction. \n
    """)
    st.markdown("<h3></h3>", unsafe_allow_html=True)

    #Setting Application sidebar default
    image = Image.open('Resources/download.jpg')
    
  
    add_selectbox = st.sidebar.selectbox(
	"App Explorer,Wanna Predict Here are Options!", ("Online", "Batch","Statistics","About"))
    st.sidebar.info('This app is created to predict Customer Churn')
    st.sidebar.image(image)

    if add_selectbox == "Online":
        st.info("Input data below")
        #Based on our optimal features selection
        
        st.subheader("Demographic data")
        
        seniorcitizen = st.selectbox('Senior Citizen:', ('Yes', 'No'))
        dependents = st.selectbox('Dependent:', ('Yes', 'No'))


        st.subheader("Payment data")
        tenure = st.slider('Number of months the customer has stayed with the company', min_value=0, max_value=72, value=0)
        contract = st.selectbox('Contract', ('Month-to-month', 'One year', 'Two year'))
        paperlessbilling = st.selectbox('Paperless Billing', ('Yes', 'No'))
        PaymentMethod = st.selectbox('PaymentMethod',('Electronic check', 'Mailed check', 'Bank transfer (automatic)','Credit card (automatic)'))
        monthlycharges = st.number_input('The amount charged to the customer monthly', min_value=0, max_value=150, value=0)
        totalcharges = st.number_input('The total amount charged to the customer',min_value=0, max_value=10000, value=0)

        st.subheader("Services signed up for")
        mutliplelines = st.selectbox("Does the customer have multiple lines",('Yes','No','No phone service'))
        phoneservice = st.selectbox('Phone Service:', ('Yes', 'No'))
        internetservice = st.selectbox("Does the customer have internet service", ('DSL', 'Fiber optic', 'No'))
        onlinesecurity = st.selectbox("Does the customer have online security",('Yes','No','No internet service'))
        onlinebackup = st.selectbox("Does the customer have online backup",('Yes','No','No internet service'))
        techsupport = st.selectbox("Does the customer have technology support", ('Yes','No','No internet service'))
        streamingtv = st.selectbox("Does the customer stream TV", ('Yes','No','No internet service'))
        streamingmovies = st.selectbox("Does the customer stream movies", ('Yes','No','No internet service'))


        data = {
                'SeniorCitizen': seniorcitizen,
                'Dependents': dependents,
                'tenure':tenure,
                'PhoneService': phoneservice,
                'MultipleLines': mutliplelines,
                'InternetService': internetservice,
                'OnlineSecurity': onlinesecurity,
                'OnlineBackup': onlinebackup,
                'TechSupport': techsupport,
                'StreamingTV': streamingtv,
                'StreamingMovies': streamingmovies,
                'Contract': contract,
                'PaperlessBilling': paperlessbilling,
                'PaymentMethod':PaymentMethod, 
                'MonthlyCharges': monthlycharges, 
                'TotalCharges': totalcharges
                }
        
        features_df = pd.DataFrame.from_dict([data])

        st.markdown("<h3></h3>", unsafe_allow_html=True)
        st.write('Overview of input is shown below')
        st.markdown("<h3></h3>", unsafe_allow_html=True)
        st.dataframe(features_df)


        #Preprocess inputs
        preprocess_df = preprocess(features_df, 'Online')

        prediction = model.predict(preprocess_df)

        if st.button('Predict'):
            if prediction == 1:
                image = Image.open("Resources/app.jpeg")
                st.warning('Yes, the customer will terminate the service.')
            else:
                st.success('No, the customer is happy with Telco Services.')

    elif(add_selectbox == "Batch"):
        # st.image('Resources/login.jpg', caption=None, width = 700, use_column_width=False)
        
        st.subheader("Dataset upload")
        uploaded_file = st.file_uploader("Choose a file")
        if uploaded_file is not None:
            data = pd.read_csv(uploaded_file)

            #Get overview of data
            st.write(data.head())
            st.markdown("<h3></h3>", unsafe_allow_html=True)

            #Preprocess inputs
            preprocess_df = preprocess(data, "Batch")

            if st.button('Predict'):
                #Get batch prediction
                prediction = model.predict(preprocess_df)
                prediction_df = pd.DataFrame(prediction, columns=["Predictions"])
                prediction_df = prediction_df.replace({1:'Yes, the customer will terminate the service.', 
                                                    0:'No, the customer is happy with Telco Services.'})
                
                st.markdown("<h3></h3>", unsafe_allow_html=True)
                st.subheader('Prediction')
                st.write(prediction_df)
    
    elif add_selectbox == "Statistics":

        #load data
        res_Data = pd.read_csv("data/Statistics.csv")
        #Drop the unwanted columns and encoding variable
        res_Data.drop(['RowNumber','CustomerId','Surname'], axis=1 ,inplace = True)

        # Spliting data
        X=res_Data[['CreditScore','Age','Balance','HasCrCard','IsActiveMember','EstimatedSalary']].values
        Y=res_Data['Exited'].values 

        pickle_in= open('notebook/Catboost.pkl', 'rb')
        classifier = pickle.load(pickle_in) 

        

        st.image('Resources/app.jpeg', caption=None, width = 700, use_column_width=False)
        CreditScore = st.slider('Credit Score',350.00 ,650.52, 850.00 )
        Age = st.slider('Age',18 ,38,92)
        Balance = st.slider('Balance',0,250898)
        EstimatedSalary = st.slider('Estimated Salary',12.00,100090.23,199992.48)
        HasCrCard = st.radio("HasCrCard",[0,1])
        IsActiveMember = st.radio("Active Member",[0,1])
        
        data = {'CreditScore': CreditScore,
                'Age': Age,
                'Balance': Balance,
                'HasCrCard':HasCrCard,
                'IsActiveMember':IsActiveMember,
                'EstimatedSalary':EstimatedSalary}        
        features = pd.DataFrame(data, index=[0])
        st.subheader('Input parameters')
        st.write(features)


        classifier.fit(X,Y)
        prediction = classifier.predict(features)
        prediction_proba = classifier.predict_proba(features)
        
        s = "Exited" 
        if (prediction_proba[0, 0] > prediction_proba[0, 1]):
            s = "Not Exited"
    
        st.set_option('deprecation.showPyplotGlobalUse', False)
        d_nc = prediction_proba[0, 0] * 360
        d_c = prediction_proba[0, 1] * 360

        make_pie([d_nc, d_c], s, [c2, c1], ['Probability(Not Exited): \n{0:.2f}%'.format(prediction_proba[0, 0] * 100),
                                            'Probability (Exited): \n{0:.2f}%'.format(prediction_proba[0, 1] * 100)])

        st.pyplot()

    else:
        st.write('*Here we are able to Find the probability of a customer churn based on their Behaviour patters which are tracked based on Daily Rendered Data.*')
        st.write('*Random Forest Classifier is used for Prediction in Early stages for Predicting Churn Rate, but later on the Algorithms were used for Visualization and focusing on Accuracy Predictions*')
        st.write('*The Catboost Classifier does the classification work where the Customer Churn Rate is based on their Credit Score Which is Assigned by the Telco Services Where Intepret the Data and Output the Statistics as Graph*')
        
        
        st.image('Resources/kmit.jpg', width = 250) 
        st.write('--BY TEAM 17')
       


def add_bg_from_local(image_file):
    with open(image_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url(data:image/{"png"};base64,{encoded_string.decode()});
        background-size: cover
    }}
    </style>
    """,
    unsafe_allow_html=True
    )

# Statistic Analysis 
def make_pie(sizes, text, colors, labels):
    col = [[i / 255. for i in c] for c in colors]
    fig, ax = plt.subplots()
    ax.axis('equal')
    width = 0.45
    kwargs = dict(colors=col, startangle=180)
    outside, _ = ax.pie(sizes, radius=1, pctdistance=1 - width / 2, labels=labels, **kwargs)
    plt.setp(outside, width=width, edgecolor='white')
    kwargs = dict(size=15, fontweight='bold', va='center')
    ax.text(0, 0, text, ha='center', **kwargs)
    ax.set_facecolor('#e6eaf1')
c1 = (226, 33, 7)
c2 = (20,20,80)


# Login and Signup Module -- TO DO
def main():
    # image = Image.open("download.jpg")
    # Configuration File
    
    with open('config.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)

    # Mapper for Authentication
    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
        config['preauthorized']
    )

    # Extracting Details
    name, authentication_status, username = authenticator.login('Login', 'main')

    if authentication_status:
        authenticator.logout('Logout', 'main')
        st.write('Welcome *%s*' % (name))
        
        authenticator.logout('Logout', 'main', key='unique_key')
    elif authentication_status == False:
        st.error('Username/password is incorrect')
    elif authentication_status == None:
        st.warning('Please enter your username and password')
   
    # if Authenticates and login Succesfully
    if st.session_state["authentication_status"]:
        
        st.write(f'Welcome *{st.session_state["name"]}*')
       
    # if Authentication is not Successed 
    # possibilites might be Invalid Credentials
    elif authentication_status is False:
        st.error('Username/password is incorrect')
        options = ['Register/Signup', 'Reset Password']
        selected_option = st.selectbox('Select an action', options)
        if selected_option == 'Register/Signup':
        # Register logic here
            try:
                if authenticator.register_user('Register user', preauthorization=False):
                    st.success('User registered successfully')
            except Exception as e:
                st.error(e)
            pass
        elif selected_option == 'Reset Password':
            # Reset password logic here
            try:
                if authenticator.reset_password(username, 'Reset password'):
                    st.success('Password modified successfully')
            except Exception as e:
                st.error(e)         
    # Possibility of Null Entry Registries
    elif st.session_state["authentication_status"] is None:
        st.warning('Please enter your username and password')

    # Updating the Configuration File 
    with open('config.yaml', 'w') as file:
        yaml.dump(config, file, default_flow_style=False)
     
if __name__ == "__main__":
    # main()
    application()   

