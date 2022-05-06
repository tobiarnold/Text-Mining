import streamlit as st
import pandas as pd
import altair as alt
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
import seaborn as sns
#import yfinance

def main():
    st.set_page_config(page_title="Twitter Elon Musk", page_icon="🚗", layout="centered")
    st.title("📈 Tweets von Elon Musk und der Tesla Aktienkurs")
    link1 = "[Elon Musk Twitter](https://twitter.com/elonmusk)"
    st.write("**Text Mining und Web Analytics**")
    st.markdown(link1, unsafe_allow_html=True)
    st.markdown("""
             - Auf der folgenden Seite werden Tweets von Elon Musk zwischen dem **02.12.2019 und dem 05.05.2022** in einem Dataframe abgebildet. 
             - Tweets die kürzer als drei Wörter waren wurden gelöscht und die Tweets mit Regular Expressions bereinigt.
             - Die Tweets wurden mit den Bibliothken **textblob** und **nltk** klassifiziert **(positive, negative und neutrale Tweets)**. 
             - Mit den verschiedenen Filtern lässt sich das Dataframe und die daraus generierten Grafiken interaktiv beinflussen. 
             - Die verschiedenen Spalten des Dataframes lassen sich mit einem Klick auf die Spaltenüberschrift absteigend oder aufsteigend sortieren.
             """)
    st.write("⚠️ Über den Filter auf der linken Seite können die verschiedenen Parameter verändert werden." 
             " Bei mobilen Geräten ist der Filter standardmäßig ausgeblendet und lässt sich mit dem Pfeil oben links aktivieren. ⚠️")
    st.markdown("""---""")
    st.title("👩‍💻 Dataframe")
    with st.sidebar.header ("Verschiedene Filtereinstellungen für den Dataframe"):
        df_choice = st.sidebar.selectbox("Dataframe mit allen Tweets (ohne Aktienkurse) oder mit Tweets und Aktienkursen (Wochenenden fallen weg)?",
        ("alle Tweets", "Tweets mit Aktienkursen"),index=1)
        if df_choice == "alle Tweets":
            df = pd.read_csv(r"https://raw.githubusercontent.com/tobiarnold/Text-Mining/main/df_all_tweets.csv", delimiter=",")
        else:
            df = pd.read_csv(r"https://raw.githubusercontent.com/tobiarnold/Text-Mining/main/df_tweets_and_stock.csv", delimiter=",")
    with st.sidebar.subheader("Optionen"):
        options = st.sidebar.multiselect("Nach welchen Wörtern soll das Dataframe gefiltert werden?",
                             ["tesla", "car","model","engine","production","lithium","battery","factory","electric"])
        options2 = st.sidebar.multiselect("Welche Sentiments sollen bei textblob beibehalten werden?",
                             ["positive", "negative", "neutral"])
        options3 = st.sidebar.multiselect("Welche Sentiments sollen bei nltk beibehalten werden?",
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
    style=(lambda x: "background-color : #90EE90" if x == "positive" else ("background-color : #FF7F7F" if x == "negative" else "background-color : #ffffa1"))
    df_download=df_option
    df_heatmap=df_option
    df_countplot=df_option
    df_wordcloud=df_option[["Text"]]
    df_option = df_option.style.applymap(style, subset=["sentiment_textblob","sentiment_nltk"])
    st.dataframe(df_option,1000,500)
    @st.cache
    def convert_df(df_download):
        return df_download.to_csv().encode('utf-8')
    csv = convert_df(df_download)
    st.download_button("Download des Dataframes",csv,"Elon_Musk_Tweets.csv","text/csv",key='download-csv')
    st.markdown("""---""")
    st.title("📊 Countplots")
    st.write("Klassifizierung mit textblob")
    textblob_positive=df_countplot.sentiment_textblob.str.count("positive").sum()
    textblob_negative=df_countplot.sentiment_textblob.str.count("negative").sum()
    textblob_neutral=df_countplot.sentiment_textblob.str.count("neutral").sum()
    st.write("Positve Labels: ",textblob_positive," Negative Labels: ",textblob_negative," Neutrale Labels: ",textblob_neutral)
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(9, 3))
    ax=sns.countplot(x ="sentiment_textblob", data = df_countplot,order = df_countplot["sentiment_textblob"].value_counts().index).set(title="Anzahl Sentiments textblob")
    st.pyplot(fig)
    st.write("Klassifizierung mit nltk")
    nltk_positive=df_countplot.sentiment_nltk.str.count("positive").sum()
    nltk_negative=df_countplot.sentiment_nltk.str.count("negative").sum()
    nltk_neutral=df_countplot.sentiment_nltk.str.count("neutral").sum()
    st.write("Positve Labels: ",nltk_positive," Negative Labels: ",nltk_negative," Neutrale Labels: ",nltk_neutral)
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(9, 3))
    ax=sns.countplot(x ="sentiment_nltk", data = df_countplot,order = df_countplot["sentiment_nltk"].value_counts().index).set(title="Anzahl Sentiments nltk")
    st.pyplot(fig)
    st.markdown("""- Die Tweets von Elon Musk werden hauptsächlich als positiv klassifiziert""")
    try:
        st.write("Anzahl der Higher und Lower Aktienwerte")
        change_higher=df_countplot["Change"].str.count("Higher").sum()
        change_lower=df_countplot["Change"].str.count("Lower").sum()
        st.write("Higher Change: ",change_higher," Lower Change: ",change_lower)
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(9, 3))
        ax=sns.countplot(x ="Change", data = df_countplot,order = df_countplot["Change"].value_counts().index).set(title="Anzahl Veränderungen des Aktienkurses")
        st.pyplot(fig)
    except:
        st.text("Bitte Dataframe Tweets mit Aktienkursen laden.")
    st.markdown("""---""")
    st.title("📚 Wordcloud")
    st.write("Die Wordcloud zeigt die häufigsten Wörter in den Tweets von Elon Musk. " 
             "Je nach Filtereinstellungen im Dataframe ändert sich die Zusammensetzung.  \n"
             "Die Anzahl der Wörter kann mit dem Slider aktiv beeinflusst werden.")
    count_wc = st.slider("Aus wie vielen Wörtern soll die Wordcloud bestehen?", 1, 100, 50)
    try:
        fig, ax1 = plt.subplots()
        text = " ".join(i for i in df_wordcloud.Text)
        stopwords_wordcloud = set(STOPWORDS)
        wordcloud = WordCloud(background_color="black", stopwords=stopwords_wordcloud,colormap = "Paired", max_words=count_wc)
        wordcloud.generate(text)
        ax1.imshow(wordcloud, interpolation="bilinear")
        ax1.axis("off")
        st.write(fig)
    except:
        st.write("Wordcloud kann nicht dargestellt werden.")
    st.markdown("""---""")
    st.title("📊 Korrelation")
    st.write("Die Heatmap zeigt die Korrelation zwischen den einzelenen nummerischen Spalten im Dataframe.  \n"
             "Die Korrelation ändert sich je nach Filtereinstellungen beim Dataframe")
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(9, 3))
    ax=sns.heatmap(df_heatmap.corr(),annot=True)
    st.write(fig)
    st.write("Leider konnte keine Korrelation zwischen den Tweets von Elon Musk und dem Tesla Aktienkurs festgestellt werden.")
    st.markdown("""---""")
    st.title("📈 Aktienkurs von Tesla")
    st.write("Die folgende Grafik zeigt den Tesla Aktienkurs zwischen dem 01.12.2019 und dem 05.05.2022")
    # get_stock_data = yf.Ticker("TSLA")
    # ticket_df = get_stock_data.history(period="1d", start="2019-12-01", end="2022-5-05")["Close"]
    # ticket_df.to_csv("ticket_df.csv")
    ticket_df = pd.read_csv(r"https://raw.githubusercontent.com/tobiarnold/Text-Mining/main/ticket_df.csv", delimiter=",")
    line = alt.Chart(ticket_df, title="Telsa Aktienkurs").mark_line().encode(x="Date:T", y="Close",
                                                                             color=alt.value("#cc0000"),
                                                                             tooltip=["Date:T",
                                                                                      "Close:Q"]).interactive()
    st.altair_chart(line, use_container_width=True)
    st.write("Der Tesla Aktienkurs hat stetig zugenommen. " 
             "Wie groß der Einluss von Elon Musk als einer der bekanntesten CEOs weltweit auf den Kursverlauf ist kann nicht abschließend erörtert werden.")
if __name__ == "__main__":
  main()
