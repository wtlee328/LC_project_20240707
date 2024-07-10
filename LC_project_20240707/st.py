import streamlit as st 
from langchain.utilities import SQLDatabase
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import os
import re

st.title("CrownSync AI")

conn = st.connection('Rolex_db', type='sql')
db = SQLDatabase.from_uri("sqlite:///Rolex_db.db")

#def get_sql(file_path,file_content):
#    with open(file_path,"wb") as f:
#        f.write(file_content)
#    return SQLDatabase.from_uri("sqlite:///"+file_path)

#if uploaded_file := st.file_uploader("Choose a database"):
#    file_c = uploaded_file.getvalue()
#    file_p = "file"
#else:
#    st.stop()

#db = get_sql(file_p, file_c)

llm = ChatOpenAI(model="gpt-4o", temperature=0.2)

def get_schema(x):
    return db.get_table_info()
def run_query(query):
    return db.run(query)
def get_sql(x):
    pattern = r"SELECT.*?;"
    match = re.search(pattern, x, re.DOTALL)
    if match:
        output = match.group().replace('\n', ' ').strip()
        return output

template ="""Based on the table structure below, write an SQL query to find all information for the model the user inquires about:
{schema}

Question: {question}"""

prompt = ChatPromptTemplate.from_template(template)

chain_sql=({"schema":RunnableLambda(get_schema),"question":RunnablePassthrough()}|prompt|ChatOpenAI()|StrOutputParser()
           |RunnableLambda(get_sql))

template_1 ="""Based on the table structure, question, SQL query, and SQL response provided, write a response:
{schema}

Question：{question}
SQL_query：{query}
SQL_response：{response}

If the input doesn't provide SQL query, reply the question using natural language."""

template_2 ="""Based on the table structure, question, SQL query, and SQL response provided, write an email response:
{schema}

Question：{question}
SQL_query：{query}
SQL_response：{response}

The email should inculde the information below:
    1.	Sender Information:
    •	Name: [Name]
    •	Position: Rolex Boutique Manager
    •	Store: [Store]
    •	Email: [Email]
    •	Location: [Location]
    2.	Client Information:
    •	Name: [ClientName]
        3.	Store Information:
    •	Store has been an Official Rolex Jeweler for over 40 years.
    4.	Product Information:
    •	Model: Rolex [Model]
    •	Features: Base on the description from SQL response
    •	Attributes:
    •	Swiss Made
    •	Highly waterproof
    •	5-year warranties
    •	Reliable and durable
    5.	Current Stock:
    •	Base on the inventory from SQL response
    6.	Invitation:
    •	Invitation to visit the showroom to see the timepiece in person.
    7.	Gratitude and Closing:
    •	Thank you for the inquiry.
    •	Hope to meet in person.
    •	Best regards.
        [Name]
        Position
        [Email]
    8.	Additional Elements:
    •	[Image][Link] (reference to an image or link provided in the email).
"""

prompt_response1 = ChatPromptTemplate.from_template(template_1)
chain_sql1=({"question":RunnablePassthrough(),"query":chain_sql}|RunnablePassthrough.assign(schema=get_schema,response=lambda x: run_query(x["query"]))|prompt_response1|ChatOpenAI())

#if input_p := st.chat_input():
#    st.chat_message("user").write(input_p)
#    res = chain_sql2.invoke(input_p)
#    st.chat_message("ai").write(res.content)

options=["Data inquiry","Email template"]
selected_option=st.selectbox("choose an option",options)

if (selected_option=="Email template"):
    st.subheader("Fill the following information") 
    MyName = st.text_input('Name', 'John Doe')
    Store = st.text_input('Store', 'Lawrenceville')
    MyEmail = st.text_input('Email', 'JohnDoe@gmail.com')
    Location = st.text_input('Location', '2207 Lawrenceville Rd, Lawrenceville, NJ 08648')
    st.markdown("####")

    rep = {
        "[Name]": MyName,
        "[Store]": Store,
        "[Email]": MyEmail,
        "[Location]": Location
    }
    rep = dict((re.escape(k), v) for k, v in rep.items()) 
    pattern = re.compile("|".join(rep.keys()))
    template_2 = pattern.sub(lambda m: rep[re.escape(m.group(0))], template_2)

    if input_p := st.chat_input():
        st.chat_message("user").write(input_p)
        prompt_response2 = ChatPromptTemplate.from_template(template_2)
        chain_sql2=({"question":RunnablePassthrough(),"query":chain_sql}|RunnablePassthrough.assign(schema=get_schema,response=lambda x: run_query(x["query"]))|prompt_response2|ChatOpenAI())
        res = chain_sql2.invoke(input_p)
        st.chat_message("ai").write(res.content)

if (selected_option=="Data inquiry"):
    if input_p := st.chat_input():
        st.chat_message("user").write(input_p)
        res = chain_sql1.invoke(input_p)
        st.chat_message("ai").write(res.content)