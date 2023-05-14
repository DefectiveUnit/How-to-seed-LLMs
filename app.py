import streamlit as st
import random
from faker import Faker
from langchain import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain

try:
    from creds import openai_key, the_password
    openai_api_key = openai_key  # Add your OpenAI API key here
except:
    openai_api_key = st.secrets["openai_api_key"]  # Add your OpenAI API key here
    the_password = st.secrets["the_password"]

save_key = openai_api_key
# Seed types
seed_types = ["Word", "Long String", "Control (No Seed)", "Small Number", "Large Number"]

random.seed(42)
number_seeds = [0,1,2,3,4,5,6,7,8,9]
big_number_seeds = [random.randint(1000000000, 9999999999) for _ in range(10)]
faker = Faker()
Faker.seed(42)
word_seeds = [faker.word() for _ in range(10)]
string_seeds = [faker.pystr(min_chars=15, max_chars=15) for _ in range(10)]

def set_seed(seed_type, word_seeds, string_seeds):
    if seed_type == "Word":
        seeds = word_seeds
    elif seed_type == "Long String":
        seeds = string_seeds
    elif seed_type == "Small Number":
        seeds = number_seeds
    elif seed_type == "Large Number":
        seeds = big_number_seeds
    else:
        seeds = [""] * 10
    return seeds

def set_long_seed(seed_type, nseeds=100):
    if seed_type == "Word":
        seeds = [faker.word() for _ in range(nseeds)]
    elif seed_type == "Long String":
        seeds = [faker.pystr(min_chars=15, max_chars=15) for _ in range(nseeds)]
    elif seed_type == "Small Number":
        seeds = [i for i in range(nseeds)]
    elif seed_type == "Large Number":
        seeds = [random.randint(1000000000, 9999999999) for _ in range(nseeds)]
    else:
        seeds = [""] * nseeds
    return seeds

prompt_template = PromptTemplate(
    input_variables=["seed", "prefix", "prompt"],
    template="""
    {prefix} {seed}

    {prompt}
    """,
)

def preview_prompt(prompt, prefix, seeds):
    formatted_prompt = prompt_template.format(seed=seeds[0], prompt=prompt, prefix=prefix)
    return formatted_prompt

def generate_output(prompt, prefix, seeds, openai_api_key):
    llm = ChatOpenAI(temperature=0, openai_api_key=openai_api_key)
    llm_chain = LLMChain(llm=llm, prompt=prompt_template)
    output_list = []
    for seed in seeds:
        output_list.append(llm_chain.run(seed=seed, prompt=prompt, prefix=prefix))
    return output_list




def main():
    # Streamlit app
    st.title("LLM Seed Game")

    # Sidebar - OpenAI API key input
    api_key = st.sidebar.text_input("OpenAI API Key", value="griggs")

    # Sidebar - OpenAI API key input and random words list
    st.sidebar.subheader("Context")
    st.sidebar.markdown("""
    In traditional code you set the seed to get a random but reproducible result. 
    LLMs let you set the temperature to 0, solving the reproducibility, but losing the randomness. 
    This is a problem if you want to run a chain a few times and get different but reproducible results (e.g. to generate many rows of dummy data).
    """)
    st.sidebar.subheader("Instructions")
    st.sidebar.markdown("""
    This app allows you to play a game to try different methods of providing seeds in the prompt for large language models. 
    Enter a prompt and a seed prefix, and select a seed type from the dropdown. 
    Then, click the **Run LLM** button which will run your prompt 10x with 10 seeds. 

    Your score is based on the number of unique outputs in the returned list.

    Let me know if you manage to get a score of 10, and how you did it! 

    https://www.linkedin.com/in/james-griggs-syd/

    Got any ideas? Raise an issue here:

    https://github.com/DefectiveUnit/How-to-seed-LLMs
    """)
    st.sidebar.subheader("Random Words")
    seed_value = st.sidebar.text_input("Enter a seed for random words/strings", value = 42)
    Faker.seed(int(seed_value))
    word_seeds = [faker.word() for _ in range(10)]
    string_seeds = [faker.pystr(min_chars=15, max_chars=15) for _ in range(10)]
    st.sidebar.subheader("Random Words")

    st.sidebar.write(word_seeds)
    st.sidebar.write(string_seeds)



    # Main content
    st.subheader("Enter your game settings:")
    prompt = st.text_input("Prompt", value = "Generate one baby name")
    prefix = st.text_input("Prefix", value = "Your mood is: ")
    seed_type = st.selectbox("Seed Type", seed_types)

    seeds = set_seed(seed_type, word_seeds, string_seeds)

    if 'score' not in st.session_state:
        st.session_state.score = 0

    if 'combined_prompt' not in st.session_state:
        st.session_state.combined_prompt = ""


    # Preview prompt button
    st.subheader("Preview Prompt")
    combined_prompt = preview_prompt(prompt, prefix, seeds)
    if st.session_state.combined_prompt != combined_prompt:
        st.session_state.score = 0
    st.session_state.combined_prompt = combined_prompt
    st.write("Combined Prompt:")
    st.code(combined_prompt)

    if 'score' not in st.session_state:
        st.session_state.score = 0

    # Generate button
    if st.button("Run LLM"):
        if not api_key:
            st.error("Please enter your OpenAI API Key")
            return
        
        # Call the generate_output function and display the loading spinner
        with st.spinner("Generating..."):
            openai_api_key = api_key  # Set the OpenAI API key
            if api_key == the_password:
                openai_api_key = save_key
            try:
                output = generate_output(prompt, prefix, seeds, openai_api_key)
            except: 
                return st.error("Error: Invalid API key (probably)")
        
        st.success("Generated successfully!")
        
        # Calculate the score based on the number of unique values in the output
        st.session_state.score = len(set(output))
        st.write("Your score:", st.session_state.score, " out of 10")
        st.write("Output:")
        st.write(output)
    

    # Display the new button if the score is 10/10
    if st.session_state.score == 10:
        st.subheader("You passed level 1 - try level 2!")
        if st.button("Run LLM (100 words/numbers)"):
            random_seeds = set_long_seed(seed_type=seed_type, nseeds=100)

            with st.spinner("Generating 100 seeds, be patient..."):
                openai_api_key = api_key  # Set the OpenAI API key
                if api_key == the_password:
                    openai_api_key = save_key
                    try:
                        output_100 = generate_output(prompt, prefix, random_seeds, openai_api_key)
                    except: 
                        return st.error("Error: Invalid API key (probably)")
                score = len(set(output_100))
                st.write("Your score:", score, " out of 100")
                st.write("Output (100 words/numbers):")
                st.write(output_100)

main()
