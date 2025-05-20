import os
from dotenv import load_dotenv
from langgraph.prebuilt import create_react_agent
from langgraph.graph import StateGraph,END
from PIL import Image
import base64
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from typing_extensions import TypedDict
load_dotenv()

agent = init_chat_model(model="gemini-2.5-flash-preview-04-17",model_provider="google_genai")

def encode_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

encoded_image = encode_image("myTruck.png")
print(encode_image)
BASE_PROMPT = "Create a content componenets for me. and {} image name {}"

class State(TypedDict):
    topic: str
    html: str
    css: str
    js: str
    
def generateHTML(state:State):
    prompt = state["topic"].format("** Generate HTML, CSS and JS structure. **","** ./screenshot.png **")
    html = agent.invoke([
        {
            "role":"system",
            "content":"""
            You are web developer. Your core foundation in HTML, CSS and Javascript. For the now your task is Create HTML, CSS and Javascript code using the image. And Your Understading about the code is highly appreciatable. You create a all component using HTML,CSS and JS. verify all the component and finally return me only without any other context code use the `svg` instead of the images. make sure you create code same as image. Make the logic based on design as well as Javascript supporter. You have good knowledge in the javascript core and DOM Manipulation. all things are organize same as same image, no one component or not any things are un organizations. in the javascript if value has `x` use `*`, if value has `÷` use `/` or etc. please use this for background work which is should work in the logics or many other things which has visualize other value and work in javascript with other symbol. to use that. and keep eye on this all informations.If given images has any backgroud image so then use image image name which is given in propmt.
            
            ## what you have to visualize in the Images:
             - visualize the `height` and `width` of the components.
             - visualize the `color` and `font` of the components.
             - visualize the `images` of the components with `height` and `width` of image and this image url `https://picsum.photos/id/237/{width}/{height}
` you can use with custom height and width **where you want to use the image**.
             - visualize the `border` and `border radius` and functionality of the image.
             - visualize the background colors of `header`,`footer`,`hero` section colors and put at the same.
            
            ## Which step you have to follow for the create components :
            
            step 1 : `analyze` the provided Image
            step 2 : Create list of `components` which is you analyzed in the image
            step 3 : Take component one and generate the apropriate code and take steps visa versa for next component with logical actions which is need in component use DOM.
            step 4 : verify the image visual and your created code if you find the any loop hole so then go to the step 1 and re write the componnet code.
            
            return without any context or any explaination
            """
        },
        {
            "role":"user",
            "content":[
                {"type":"text","text":prompt},
                {"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{encoded_image}"}}
            ]
            # "content":f"{prompt} , this is data of image data:image/jpeg;base64,{encoded_image}"
        }
    ])
    with open("index.html","w") as f:
        f.write(html.content)
    return {"html":html.content}

# generateHTML()""
workflow = StateGraph(State)

workflow.add_node("generate",generateHTML)
workflow.set_entry_point("generate")
workflow.add_edge("generate",END)

graph = workflow.compile()
state = graph.invoke({"topic": "Generate the code using this image","html":"","css":"","js":""})

