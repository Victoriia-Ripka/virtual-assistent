# from transformers import pipeline
from transformers import AutoTokenizer, TFRobertaForQuestionAnswering, pipeline

tokenizer = AutoTokenizer.from_pretrained("robinhad/ukrainian-qa")
model = TFRobertaForQuestionAnswering.from_pretrained("robinhad/ukrainian-qa", from_pt=True)

question_answering = pipeline("question-answering", model=model, tokenizer=tokenizer)

# answer = pipeline(model="robinhad/ukrainian-qa")

question = "Де ти живеш?"
context = "Мене звати Сара і я живу у Лондоні"
answer = question_answering({'question': question, 'context': context})
print(answer['answer'])
# print(answer(question=question, context=context)["answer"].strip())

# result = qa_model(question = question, context = context)
# model_name = "robinhad/ukrainian-qa"
# tokenizer = AutoTokenizer.from_pretrained(model_name)
# model = AutoModelForQuestionAnswering.from_pretrained(model_name)
# qa_model = pipeline("question-answering", model=model.to("cpu"), tokenizer=tokenizer)