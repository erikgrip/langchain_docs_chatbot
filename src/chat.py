import ssl

import nltk
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA, LLMChain
from langchain.llms.openai import OpenAI

from src.data_downloader.run import download_repo
from src.doc_store.doc_store import DocStore

# HACK: https://github.com/gunthercox/ChatterBot/issues/930#issuecomment-322111087
try:
    _create_unverified_https_context = (
        ssl._create_unverified_context  # pylint: disable=protected-access
    )
except AttributeError:
    pass
else:
    ssl._create_default_https_context = (  # pylint: disable=protected-access
        _create_unverified_https_context
    )

nltk.download("punkt")


download_repo()
doc_store = DocStore()
llm = OpenAI(temperature=0)


def dummy_chain():
    """Answer an example question using a LLM chain."""
    template = """\
    Context: Two tomatoes were crossing a road when one of \
    them suddenly got run over by a truck. Then the other \
    tomato said: come on ketchup, lets go.

    Question: {question}

    Answer:
    """

    question = "What is funny about this joke?"
    prompt = PromptTemplate(template=template, input_variables=["question"])
    llm_chain = LLMChain(prompt=prompt, llm=llm)
    llm_chain.run({"question": question})


def run_chat(model, document_store):
    """Answer a question with document store search."""
    question = "What vector store classes are currently available?"
    qa_chain = RetrievalQA.from_chain_type(
        model, retriever=document_store.db.as_retriever(search_kwargs={"k": 25})
    )
    answer = qa_chain({"query": question})
    print(answer)


# doc_store.db_from_docs_dir("data/unzipped/langchain-master/docs")
run_chat(llm, doc_store)
