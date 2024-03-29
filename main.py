import requests
import csv
import time
import os
import urllib.request
import re
from bs4 import BeautifulSoup
from shutil import copyfileobj

class Scrap:
        
    def __init__(self, url_home_page):
        self.url_home_page = url_home_page
    
    def creation_dir(self, choice_categorie):
        if not os.path.exists("books"):
            os.makedirs("books")
            
        for title, url in choice_categorie.items():   
            if not os.path.exists("books/" + title):
                os.makedirs("books/" + title)
            
    def take_url_and_category_page(self):
        page = requests.get(self.url_home_page)
        html = BeautifulSoup(page.content, "html.parser")
        list_page = html.find(class_="nav-list").find_all("a")
        list_extrat = {}
        
        for page in list_page:
            list_extrat[page.string.strip()] = "http://books.toscrape.com/" + page["href"]
            
        return list_extrat
        
    def take_url_book_page(self, url_of_the_page, list_urls_book_page):
        page = requests.get(url_of_the_page)
        html = BeautifulSoup(page.content, "html.parser")
        balise = html.find_all("h3")

        if url_of_the_page[0:52] == "http://books.toscrape.com/catalogue/category/books_1":
            for element in balise:
                url = element.find("a")["href"]
                list_urls_book_page.append("http://books.toscrape.com/catalogue/" + url[6:])
        else:
            for element in balise:
                url = element.find("a")["href"]
                list_urls_book_page.append("http://books.toscrape.com/catalogue/" + url[9:])

        try:
            var = html.find(class_="next").find("a").string
        except:
            var = ''

        if var == "next":
            i = 0
            for lettre in range(len(url_of_the_page)): 
                if url_of_the_page[- i] == "/":
                    self.take_url_book_page(url_of_the_page[: -i] + "/" + html.find(class_="next").find("a")["href"], list_urls_book_page)
                    break
                i += 1
                
        return list_urls_book_page
        
    def extract_information_book(self, list_urls_book_page):
        list_info_book = []
        for url_this_book in list_urls_book_page:
            print(url_this_book)
            page = requests.get(url_this_book)
            html = BeautifulSoup(page.content, "html.parser")

            lien_product_information = html.find(class_="table-striped").find_all("tr")
            list_product_information = []
            for information in lien_product_information:
                list_product_information.append(information.find("td").string)

            universal_produc_code = list_product_information[0]
            price_excluding_tax = list_product_information[2]      
            price_including_tax = list_product_information[3]  
            number_available = list_product_information[5]
            
            review_rating = html.find(class_="star-rating")["class"][1]

            lien_category = html.find(class_="breadcrumb").find_all("li")
            list_category = []
            for info in lien_category:
                list_category.append(info.find("a"))

            category = list_category[2].string
            try:
                product_description = html.find(id="product_description").find_next("p").string
            except:
                product_description = "none"
                
            title = html.find(class_="product_main").find("h1").string
            product_page_url = url_this_book
            image_url = "http://books.toscrape.com" + html.find(class_="carousel-inner").find("img")["src"][5:]

            list_info_book.append([product_page_url, universal_produc_code, title, price_including_tax, price_excluding_tax, number_available, product_description, category, review_rating, image_url])
        
        return list_info_book
        
    def save_in_csv(self, name_file, list_info_book):
        date = str(time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime()))
        header = ["product_page_url", "universal_produc_code", "title", "price_including_tax", "price_excluding_tax", "number_available", "product_description", "category", "review_rating", "image_url"] 
        destination_file = "./books/" + name_file + "/" +  name_file + '_' + date + "/"
        destination_csv = destination_file + name_file + '_' + date + ".csv"
        os.makedirs(destination_file)
        self.save_img(list_info_book, destination_file)
        with open(destination_csv, "w", encoding='utf-8') as fichier_CSV:
            writer = csv.writer(fichier_CSV, delimiter=",")
            writer.writerow(header)

            for book in list_info_book:
                writer.writerow(book)
    
    def save_img(self, list_info_book, destination_download): 
            for image in list_info_book:
                new_title = re.sub('\/|\:|\*|\?|\"|\>|\<|\|', '', image[2])
                print("Save image " + new_title)
                urllib.request.urlretrieve(image[9], destination_download + new_title + ".jpg")


class Screen(Scrap):
    def __init__(self, url_home_page):
        super().__init__(url_home_page)
        
    def display_play(self, error):
        list_category = self.take_url_and_category_page()
        self.display_list(list_category, error)
        selection_category = input()

        if len(selection_category) > 2 or selection_category.replace(" ", "").isalpha() or int(selection_category) > len(list_category) - 1 or int(selection_category) < 0:
            self.display_play(True)
        else:
            url_selection = self.take_url_selection(list_category, selection_category)
            print(url_selection)
            return url_selection
        
    def display_list(self, list_category, error):
        i = 0       
        if error == True:
            print("Le chiffre sélectionné n'est pas valide")
            print("Veuillez en choisir un valide")   
        elif error ==  False:
            for title_page, url in list_category.items():
                print(i, title_page)
                i += 1
            print("Veuillez sélectionner le chiffre de la catégory ")
            print("Ou 0 pour tout sélectionner ")
            
    
    def take_url_selection(self, list_category, selection_category):
        i = 0
        if int(selection_category) == 0:
            list_category.pop("Books")
            return list_category
        else:
            for title_page, url in list_category.items():
                if i == int(selection_category):
                    return {title_page: url}
                i += 1
        
def start_scrape():
    start = Screen("http://books.toscrape.com/index.html")
    choice_categorie = start.display_play(False)
    start.creation_dir(choice_categorie)
    
    for title, url_page in choice_categorie.items():
        list_url_book = start.take_url_book_page(url_page, [])
        print(len(list_url_book), "Book in the catégory " + title)
        list_info_book = start.extract_information_book(list_url_book)
        start.save_in_csv(title, list_info_book)
        print("End")

start_scrape()