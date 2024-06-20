from flask import Flask, jsonify, render_template, request
import google.generativeai as genai
from bs4 import BeautifulSoup
import requests
import sqlite3
import os

genai.configure(api_key='AIzaSyASqvoV2aRtb0_IXfsRvTKViSdZXLsTOBM')  # Replace 'YOUR_API_KEY' with your actual API key
gemini_model = genai.GenerativeModel('gemini-pro')
chat = gemini_model.start_chat(history=[])

connection = sqlite3.connect('user_data.db')
cursor = connection.cursor()

command = """CREATE TABLE IF NOT EXISTS user(name TEXT, password TEXT, mobile TEXT, email TEXT)"""
cursor.execute(command)

app = Flask(__name__)
chat_history = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home')
def home():
    return render_template('userlog.html')

@app.route('/userlog', methods=['GET', 'POST'])
def userlog():
    if request.method == 'POST':

        connection = sqlite3.connect('user_data.db')
        cursor = connection.cursor()

        name = request.form['name']
        password = request.form['password']

        query = "SELECT name, password FROM user WHERE name = '"+name+"' AND password= '"+password+"'"
        cursor.execute(query)

        result = cursor.fetchall()

        if result:
            return render_template('userlog.html')
        else:
            return render_template('index.html', msg='Sorry, Incorrect Credentials Provided,  Try Again')
    return render_template('index.html')


@app.route('/userreg', methods=['GET', 'POST'])
def userreg():
    if request.method == 'POST':

        connection = sqlite3.connect('user_data.db')
        cursor = connection.cursor()

        name = request.form['name']
        password = request.form['password']
        mobile = request.form['phone']
        email = request.form['email']
        
        print(name, mobile, email, password)

        command = """CREATE TABLE IF NOT EXISTS user(name TEXT, password TEXT, mobile TEXT, email TEXT)"""
        cursor.execute(command)

        cursor.execute("INSERT INTO user VALUES ('"+name+"', '"+password+"', '"+mobile+"', '"+email+"')")
        connection.commit()

        return render_template('index.html', msg='Successfully Registered')
    
    return render_template('index.html')

@app.route('/analyse', methods=['GET', 'POST'])
def analyse():
    if request.method == 'POST':
        user_input = request.form['query']
        print(user_input)
        img_path = None

        # Search for images related to the user input
        search_url = f'https://www.google.com/search?q={user_input}&tbm=isch'
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(search_url, headers=headers)
        print(response.content)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            img_tags = soup.find_all('img')
            print(img_tags)
            if img_tags:
                img_url = img_tags[1].get('src')
                img_path = img_url
                print(img_path)
        
        gemini_response = chat.send_message('description for '+user_input+' in paragraph')
        print(gemini_response.text)
                
        return render_template('userlog.html', img_path=img_path, data=gemini_response.text)

    return render_template('userlog.html')

@app.route('/logout')
def logout():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)

