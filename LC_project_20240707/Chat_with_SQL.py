from langchain_community.utilities import SQLDatabase
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate

db = SQLDatabase.from_uri("sqlite:///Rolex_db.db")
llm = ChatOpenAI(model="gpt-4o", temperature=0.5)

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

Question: {question}
The response of the SQL query should have the following structure:
```SELECT
...
```"""
prompt = ChatPromptTemplate.from_template(template)

chain_sql=({"schema":RunnableLambda(get_schema),"question":RunnablePassthrough()}|prompt|ChatOpenAI()|StrOutputParser()
           |RunnableLambda(get_sql))


template_1 ="""Based on the table structure, question, SQL query, and SQL response provided, write an email response:
{schema}

Question：{question}
SQL_query：{query}
SQL_response：{response}

The email should follow the structure below:
    1.	Sender Information:
    •	Name: [MyName]
    •	Position: Rolex Boutique Manager
    •	Store: [Store]
    •	Email: [MyEmail]
    •	Location: [Store] [Location]
    2.	Client Information:
    •	Name: [ClientName]
        3.	Store Information:
    •	Store has been an Official Rolex Jeweler for over 40 years.
    •	Address: [Address]
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
    8.	Additional Elements:
    •	[Image][Link] (reference to an image or link provided in the email).
"""
prompt_response = ChatPromptTemplate.from_template(template_1)

chain_sql2=({"question":RunnablePassthrough(),"query":chain_sql}|RunnablePassthrough.assign(schema=get_schema,response=lambda x: run_query(x["query"]))|prompt_response|ChatOpenAI())

reply = chain_sql2.invoke("Hi I am interested in sporty styles. I am wondering if there's any available.")

print(reply)