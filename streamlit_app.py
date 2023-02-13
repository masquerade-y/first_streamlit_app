import streamlit
import pandas as pd
import requests
import snowflake.connector
from urllib.error import URLError

# app outline
streamlit.title('My Parents New Healthy Diner')

streamlit.header('Breakfast Favorites')
streamlit.text('🥣 Omega 3 & Blueberry Oatmeal')
streamlit.text('🥗 Kale, Spinach & Rocket Smoothie')
streamlit.text('🐔 Hard-Boiled Free-Range Egg')
streamlit.text('🥑🍞 Avocado Toast')

streamlit.header('🍌🥭 Build Your Own Fruit Smoothie 🥝🍇')


# import data
my_fruit_list = pd.read_csv("https://uni-lab-files.s3.us-west-2.amazonaws.com/dabw/fruit_macros.txt")

# reset index
my_fruit_list = my_fruit_list.set_index('Fruit')

# put a pick list here so they can pick the fruit they want to include
fruits_selected = streamlit.multiselect("Pick some fruits:",   \
                                        list(my_fruit_list.index),   \
                                        ['Avocado', 'Strawberries'])  # default fruits
fruits_to_show = my_fruit_list.loc[fruits_selected]

# display data as a table on the page
streamlit.dataframe(fruits_to_show)


# create the repeatable code block (called a function)
def get_fruityvice_data(fruit_choice):
    streamlit.write('The user entered ', fruit_choice, '.')
    fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" + fruit_choice)

    # take the json version of the response and normalize it
    fruityvice_normalized = pd.json_normalize(fruityvice_response.json())
    
    return fruityvice_normalized

# call the Fruityvice API
streamlit.header("Fruityvice Fruit Advice!")

try:
    # add a text box to display fruityvice api response
    fruit_choice = streamlit.text_input('What fruit would you like information about?')
    
    if not fruit_choice:
        streamlit.error("Please select a fruit to get information")
    else:
        fruit_data = get_fruityvice_data(fruit_choice)

        # display the table
        streamlit.dataframe(fruit_data)

except URLError as e:
    streamlit.error()
    
# don't run anything past here while we troubleshoot
#streamlit.stop()

# connect to snowflake
streamlit.header("View Our Fruit List & Add Your Favorites!")

# function to pull fruit list from snowflake
def get_fruit_load_list():
    with my_cnx.cursor() as my_cur:
        my_cur.execute("SELECT * FROM FRUIT_LOAD_LIST")
        return my_cur.fetchall()

# function to allow the end user to add a fruit to the list
def insert_row_snowflake(new_fruit):
    with my_cux.cursor() as my_cur:
        my_cur.execute("INSERT INTO FRUIT_LOAD_LIST VALUES ('" + new_fruit + "')")
        return "Thanks for adding " + new_fruit + "!"

# add a button to load the fruit list
if streamlit.button('Get fruit list'):
    my_cnx = snowflake.connector.connect(**streamlit.secrets["snowflake"])
    freuit_list = get_fruit_load_list()
    streamlit.markdown("**The fruit load list contains:**")
    streamlit.dataframe(freuit_list)
    
    # add a text box to allow user to add a fruit
    fruit_added = streamlit.text_input('What fruit would you like to add?')
    returned_text = insert_row_snowflake(fruit_added)
    streamlit.text(returned_text)
    my_cur.close()
