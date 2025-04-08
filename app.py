from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import logging
import pymongo

logging.basicConfig(filename="scrapper.log" , level=logging.INFO)

app = Flask(__name__)

@app.route("/", methods = ['GET'])
@cross_origin()
def homepage():
    return render_template("index.html")

@app.route("/review" , methods = ['POST' , 'GET'])
@cross_origin()
def index():
    if request.method == 'POST':
        try:
            searchString = request.form['content'].replace(" ","")
            flipkart_url = "https://www.flipkart.com/search?q=" + searchString
            uClient = uReq(flipkart_url)
            flipkartPage = uClient.read()
            uClient.close()
            flipkart_html = bs(flipkartPage, "html.parser")
            # bigboxes = flipkart_html.findAll("div", {"class": "_1AtVbE col-12-12"})
            bigboxes = flipkart_html.findAll("a", {"class":"CGtC98"})
            # del bigboxes[0:3]
            box = bigboxes[0]
            productLink = "https://www.flipkart.com" + box["href"]


            prodRes = requests.get(productLink)
            prodRes.encoding='utf-8'
            
            prod_html = bs(prodRes.text, "html.parser")
            print(prod_html)
            commentboxes = prod_html.find_all("div", {"class":"col EPCmJX"})

            filename = searchString + ".csv"
            fw = open(filename, "w")
            headers = "Product, Customer Name, Rating, Heading, Comment \n"
            fw.write(headers)
            reviews = []
            for commentbox in commentboxes:
                try:
                    #name.encode(encoding='utf-8')
                    name = commentbox.find_all("p", {"class":"_2NsDsF AwS1CA"})[0].text

                except:
                    logging.info("name")

                try:
                    #rating.encode(encoding='utf-8')
                    rating = commentbox.div.div.text


                except:
                    rating = 'No Rating'
                    logging.info("rating")

                try:
                    #commentHead.encode(encoding='utf-8')
                    commentHead = commentbox.div.p.text

                except:
                    commentHead = 'No Comment Heading'
                    logging.info(commentHead)



                try:
                    comtag = commentbox.find_all("div", {"class":""})[0].div.text
                    #custComment.encode(encoding='utf-8')
                    custComment = comtag
                except Exception as e:
                    logging.info(e)

                mydict = {"Product": searchString, "Name": name, "Rating": rating, "CommentHead": commentHead,
                          "Comment": custComment}
                reviews.append(mydict)
            logging.info("log my final result {}".format(reviews))

            client = pymongo.MongoClient("mongodb://localhost:27017/")
            db = client['review_scrap']
            review_col = db['review_data']
            review_col.insert_many(reviews)

            return render_template('result.html', reviews=reviews[0:(len(reviews)-1)])
        except Exception as e:
            logging.info(e)
            return 'something is wrong'
    # return render_template('results.html')

    else:
        return render_template('index.html')


if __name__=="__main__":
    app.run(host="127.0.0.1",port=5000, debug=True)
