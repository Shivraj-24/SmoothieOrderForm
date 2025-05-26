# Import python packages
import streamlit as st
import requests
from snowflake.snowpark.functions import col

# Write directly to the app
st.title(f":cup_with_straw: Customize your Smoothie! :cup_with_straw:")
st.write("""Choose the fruit you want in your custom Smoothie!""")

name_on_order = st.text_input("Name on Smoothie:")  
st.write("The name on the Smoothie will be:", name_on_order)

cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))
pd_df = my_dataframe.to_pandas()

ingredients_list = st.multiselect('Choose upto 5 ingredients:', my_dataframe)

if ingredients_list:
    ingredients_string = ''
    for fruit_chosen in ingredients_list:
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write(f'The search value for {fruit_chosen}, is {search_on}.')
        st.subheader(f"{fruit_chosen} Nutrition information")
        smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")
        sf_df = st.dataframe(smoothiefroot_response.json(), use_container_width=True)
        ingredients_string += fruit_chosen + ' '
    submit_btn = st.button("Submit Order")
    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
            values ('""" + ingredients_string + """', '""" + name_on_order + """')"""
    
    if submit_btn and ingredients_string:
        try:
            session.sql(my_insert_stmt).collect()
            st.success('Your Smoothie is ordered, ' + name_on_order.title() + '!', icon="✅")
        except:
            st.write('Something went wrong. Try again later!')
        






