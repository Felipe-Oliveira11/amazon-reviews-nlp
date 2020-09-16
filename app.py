import streamlit as st
from inference import review_predict


# main menu
def menu():

    st.sidebar.header('Home')
    page = st.sidebar.radio("", ('Amazon',
                                 'Deep learning application',
                                 'Review sentiment',
                                 'Contact'))
    hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)

    if page == 'Amazon':
        amazon()

    if page == 'Deep learning application':
        plataform()

    if page == 'Review sentiment':
        sentiment()

    if page == 'Contact':
        contact()


# Amazon page
def amazon():
    st.title('Amazon')
    st.write('')
    st.image(
        'https://jpimg.com.br/uploads/2018/09/amazon-1024x683.png',
        width=500,
        height=500)


# Amazon Deep learning
def plataform():
    st.title('Deep learning Application')
    st.write('This application is builded using Deep learning model and main objective is to be able that The Amazon obtain informations \
        about sentiments their users and your sentiments relantionship on music product, in real-time making inference Reviews in this plataform')
    st.write('\n')
    st.image('https://blog.vindi.com.br/wp-content/uploads/2017/03/a-amazon-vai-engolir-o-varejo-tradicional.jpg',
             width=600,
             height=300)
    st.write('\n')
    st.write('The model that´s running in backend this application it has architecture is LSTM with Embeddings, The model was trained through on Google Colab, in dataset where contains over ten thousands of reviews in music section, for most informations about this solution: https://github.com/Felipe-Oliveira11/amazon-reviews-nlp')


# Sentiment Prediction
def sentiment():
    st.title(
        'Review sentiment')
    st.image(
        'https://review.chinabrands.com/chinabrands/seo/image/20190226/buyamazonreviews.jpg',
        width=500,
        height=200)
    st.write('\n')
    st.write('\n')
    st.write('\n')

    # insert review
    review = st.text_input('Insert Review', max_chars=280)
    if st.button('Predict Sentiment'):
        prediction = review_predict(review)
        if prediction == 2:
            st.success('Review sentiment: Positive')
        elif prediction == 1:
            st.success('Review Sentiment: Neutral')
        else:
            st.success('Review sentiment: Negative')


# contato
def contact():
    st.title('Contact')
    st.image('https://encrypted-tbn0.gstatic.com/images?q=tbn%3AANd9GcSh8_BbTxZSsHWdLsSVjvVGVjASl3WynpmbMg&usqp=CAU',
             width=100, height=100)
    st.write('\n')
    st.write('\n')
    st.write('This project was develop by Felipe Oliveira, \
             Questions or suggestions send me a message in e-mail or LinkedIn.')
    st.write('\n')
    st.markdown(
        '[LinkedIn](https://www.linkedin.com/in/felipe-oliveira-18a573189/)')
    st.write('\n')
    st.write('E-mail: felipe.oliveiras2000@gmail.com')


if __name__ == '__main__':
    menu()
