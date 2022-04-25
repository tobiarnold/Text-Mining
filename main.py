import streamlit as st
from streamlit import cli as stcli
import pandas as pd
import altair as alt
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
import seaborn as sns

def main():
    st.set_page_config(page_title="Twitter Elon Musk", page_icon="🚗", layout="wide")
    st.title("Tweets von Elon Musk und der Tesla Aktienkurs")
    link1 = "[Elon Musk Twitter](https://twitter.com/elonmusk)"
    st.markdown(link1, unsafe_allow_html=True)
    st.write("**Text Mining und Web Analytics**")
    st.write("Auf der folgenden Seite werden Tweets von Elon Musk zwischen dem **02.12.2019 und dem 22.04.2022** in einem Dataframe abgebildet. "
             "Tweets die kürzer als drei Wörter waren wurden gelöscht.  \n"
             "Die Tweets wurden mit den Bibliothken textblob und nltk klassifiziert. "
             "Mit den verschiedenen Filtern lässt sich das Dataframe und die daraus generierten Grafiken interaktiv beinflussen")
    st.markdown("##### Verschiedene Filtereinstellungen für den Dataframe")
    df_choice = st.selectbox("Dataframe mit allen Tweets oder mit Tweets und Aktienkursen (Wochenenden fallen weg)?",
        ("alle Tweets", "Tweets mit Aktienkursen"),index=1)
    if df_choice == "alle Tweets":
        df = pd.read_csv(r"https://raw.githubusercontent.com/tobiarnold/Text-Mining/main/df_all_tweets.csv", delimiter=",")
    else:
        df = pd.read_csv(r"https://raw.githubusercontent.com/tobiarnold/Text-Mining/main/tweets_streamlit.csv", delimiter=",")
    options = st.multiselect("Nach welchen Wörtern soll das Dataframe gefiltert werden?",
                             ["tesla", "car","model","engine","production","lithium","battery","factory","electric"])
    options2 = st.multiselect("Welche Sentiments sollen bei textblob beibehalten werden?",
                             ["positive", "negative", "neutral"])
    options3 = st.multiselect("Welche Sentiments sollen bei nltk beibehalten werden?",
                              ["positive", "negative", "neutral"])
    df_option=df
    option = st.radio("Sollen bei den Sentiment Spalten nur gleiche Klassifizierungen behalten werden?", ("Ja", "Nein"),index=1)
    if option == "Ja":
        cols = ["sentiment_textblob", "sentiment_nltk"]
        df_option["new_sentiment"] = df_option[cols].eq(df_option[cols[0]], axis=0).all(axis=1)
        df_option = df_option[df_option.new_sentiment]
        df_option = df_option.drop(columns="new_sentiment")
    else:
        pass
    df_option = df_option[df_option["Text"].str.contains('|'.join(options))]
    df_option = df_option[df_option["sentiment_textblob"].str.contains('|'.join(options2))]
    df_option = df_option[df_option["sentiment_nltk"].str.contains('|'.join(options3))]
    style=(lambda x: "background-color : green" if x == "positive" else ("background-color : red" if x == "negative" else "background-color : yellow"))
    df_heatmap=df_option
    df_wordcloud=df_option[["Text"]]
    df_option = df_option.style.applymap(style, subset=["sentiment_textblob","sentiment_nltk"])
    st.dataframe(df_option)
    st.title("📚 Wordcloud")
    count_wc = st.slider("Aus wie vielen Wörtern soll die Wordcloud bestehen?", 1, 100, 50)
    try:
        fig, ax1 = plt.subplots()
        text = " ".join(i for i in df_wordcloud.Text)
        stopwords_wordcloud = set(STOPWORDS)
        wordcloud = WordCloud(background_color="black", stopwords=stopwords_wordcloud,colormap = 'Paired', max_words=count_wc)
        wordcloud.generate(text)
        ax1.imshow(wordcloud, interpolation="bilinear")
        ax1.axis("off")
        st.write(fig)
    except:
        st.write("Wordcloud kann nicht dargeastellt werden.")
    st.title("📊 Korrelation")
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(9, 3))
    ax=sns.heatmap(df_heatmap.corr(),annot=True)
    st.write(fig)
    st.title("📈 Aktienkurs von Tesla")
    # get_stock_data = yf.Ticker("TSLA")
    # ticket_df = get_stock_data.history(period="1d", start="2019-9-26", end="2022-8-04")["Close"]
    # ticket_df.to_csv("ticket_df.csv")
    ticket_df = pd.read_csv(r"https://raw.githubusercontent.com/tobiarnold/Text-Mining/main/ticket_df.csv", delimiter=",")
    line = alt.Chart(ticket_df, title="Telsa Aktienkurs").mark_line().encode(x="Date:T", y="Close",
                                                                             color=alt.value("#cc0000"),
                                                                             tooltip=["Date:T",
                                                                                      "Close:Q"]).interactive()
    st.altair_chart(line, use_container_width=True)
if __name__ == "__main__":
  main()
