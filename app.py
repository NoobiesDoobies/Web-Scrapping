from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from bs4 import BeautifulSoup 
import requests
import re 

#don't change this
matplotlib.use('Agg')
app = Flask(__name__) #do not change this

#insert the scrapping here
url_get = requests.get('https://www.imdb.com/search/title/?release_date=2021-01-01,2021-12-31')
soup = BeautifulSoup(url_get.content,"html.parser")

#find your right key here
table = soup.find("div", attrs={"class":"lister-list"})
datas = table.findAll("div", attrs={"class" : "lister-item mode-advanced"})
row_length = len(datas)

temp = [] #initiating a list 


#insert the scrapping process here
for i in range (row_length):
    index = int(datas[i].find("span", attrs={"class" : "lister-item-index unbold text-primary"}).text.replace(".","").strip())
    name = datas[i].find("h3", attrs={"class" : "lister-item-header"}).find("a").text.strip()
    year = datas[i].find("span", attrs={"class" : "lister-item-year text-muted unbold"}).text.replace("(", "").replace(")", "").strip()
    imdb_rating = datas[i].find("strong").text.strip()
    votes = datas[i].find("span", attrs={"name" : "nv"}).text.replace(",", "").strip()
    metascore_tag = datas[i].find("span", attrs={"class" : re.compile("metascore")})
    if(metascore_tag != None):
        metascore=metascore_tag.text.strip()
    else:
        metascore=""
    temp.append((index,name, year,imdb_rating,votes,metascore))

temp = temp[::-1]

#change into dataframe
df = pd.DataFrame(temp, columns=["Ranking", "Name", "Year", "IMDB_Rating", "Votes", "MetaScore"]).set_index("Ranking")

#insert data wrangling here

df["Year"] = df["Year"].astype("category")
df["IMDB_Rating"] = df["IMDB_Rating"].astype("float")
df["Votes"] = df["Votes"].astype("int")
df["MetaScore"] = df["MetaScore"].str.extract('(\d+)', expand=False).astype("float")

#end of data wranggling 

@app.route("/")
def index(): 
	
	card_data = f'{df["IMDB_Rating"].mean().round(2)}' #be careful with the " and ' 

	# generate plot
	ax = df.plot(figsize = (20,9)) 
	
	# Rendering plot
	# Do not change this
	figfile = BytesIO()
	plt.savefig(figfile, format='png', transparent=True)
	figfile.seek(0)
	figdata_png = base64.b64encode(figfile.getvalue())
	plot_result = str(figdata_png)[2:-1]

	# render to html
	return render_template('index.html',
		card_data = card_data, 
		plot_result=plot_result
		)


if __name__ == "__main__": 
    app.run(debug=True)