import concurrent.futures
from dotenv import load_dotenv
from srcreader import SrcReader
from wantedpt import WantedChatCompletions, run_completions

load_dotenv()

question = "가슴이 너무 작아서 고민이야."

srcs = SrcReader("./src/*.json")
search_keyword_chain = WantedChatCompletions("f803a97aa734c16ded979d5b176389bf80b7bd2230ee5c49ef94dd6c7df8cae2")
document_index_search_chain = WantedChatCompletions("1cbab7a71f89a0f4a1874c9b0c8abdc829164e44254614b856f8013d0c6d1bc5")
generation_chain = WantedChatCompletions("47df1957fb5093fc089887263481f3a4ab1551fc1ea5dcbe29ba27c8f3d30241")

with concurrent.futures.ThreadPoolExecutor() as executor:
    future_keyword = executor.submit(run_completions, search_keyword_chain, {"question": question})
    future_doc_index = executor.submit(run_completions, document_index_search_chain, {"question": question})

    keyword = future_keyword.result()
    doc_index = future_doc_index.result()

doc = srcs.get_document(index=keyword)
context = srcs.get_paragraph(doc, index=doc_index)
answer = generation_chain.completions(params={"context": context, "question": question})
print(answer)