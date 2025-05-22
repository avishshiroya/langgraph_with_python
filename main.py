import os
from dotenv import load_dotenv
from langgraph.prebuilt import create_react_agent
from langgraph.graph import StateGraph,END
from PIL import Image
import base64
from typing import Optional
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field
from typing_extensions import TypedDict
load_dotenv()

agent = init_chat_model(model="gemini-2.5-flash-preview-04-17",model_provider="google_genai")

def encode_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

encoded_image = encode_image("AstraLink-05-22-2025_12_43_PM.png")
BASE_PROMPT = "Create a content componenets for me. and {} image name {}"

class CodeBlock(TypedDict):
    html: str
    css: str
    js: str

class State(TypedDict):
    topic: str
    data: str
    
class ResponseFormatter(BaseModel):
    """Always use this tool to structure your response to the user."""
    html: str = Field(description="HTML Code")
    css: Optional[str] = Field(default="", description="CSS Code")
    js: Optional[str] = Field(default="", description="Javascript Code")

structured_llm = agent.with_structured_output(ResponseFormatter)

def generateHTML(state:State):
    prompt = state["topic"].format("** Generate HTML, CSS and JS structure. **","** ./screenshot.png **")
    print(f"your prompt is {prompt} . Wait For Generation....")
    html = agent.invoke([
        {
            "role":"system",
            "content":"""
            Your name is **kenil**. Kenil you are web developer. Your core foundation in HTML, CSS. and Javascript. For the now your task is Create HTML, CSS and Javascript code using the image. And Your Understading about the code is highly appreciatable. You create a all component using HTML,CSS and JS. verify all the component and finally return me only without any other context code use the `svg` instead of the images. make sure you create code same as image. Make the logic based on design as well as Javascript supporter. You have good knowledge in the javascript core and DOM Manipulation. all things are organize same as same image, no one component or not any things are un organizations. in the javascript if value has `x` use `*`, if value has `÷` use `/` or etc. please use this for background work which is should work in the logics or many other things which has visualize other value and work in javascript with other symbol. to use that. and keep eye on this all informations.If given images has any backgroud image so then use image image name which is given in propmt.
            
            ## what you have to visualize in the Images:
             - visualize the compoenents `width` and `height` then make list of the needed `height and width`,`position like : center,left,right,up,down`,`color`,`font`,`images`,`text` use this list for create components
             - visualize the `height` and `width` of the components.
             - visualize the `color` and `font` of the components.
             - visualize the `images` of the components with `height` and `width` of image and this image url `https://picsum.photos/id/{random}/{width}/{height}
` you can use with custom height and width. you have to give `001 to 999` random number.  **where you want to use the image**.
             - visualize the `border` and `border radius` and functionality of the image.
             - visualize the background colors of `header`,`footer`,`hero` section colors and put at the same.
             - visulaize the `videos` for background and other components. use this link **https://www.pexels.com/video/a-cloud-of-paint-underwater-7565439/** this link for video.
             - visualize the component `height - width` with `margin - padding` and remember the position of buttons and text also.
             - visualize the hover effects or animations for components or backgroud. with you can other libraries for make component animated if needed.
             - visualize the dropdown option and make appropriate page buttons in dropdown
             - use the `font-awesome CDN` for icons.
             - **PRIORITY for mic icon ** : if you visualize the mic icon ask the user for the mic permissions.
             - **PRIORITY for input type file ** : add functionality to user can add file.
             - visualize the `setting`,`user profile` and `new` buttons or icons open the details model appropriatly icon type.
             - visualize the `sidebar` or `side menus` with the `collapse icon` create a functionality to hide or show the side bar with the haep of JQuery.
             - **PRIORITY for chat components** : visualize the images is looking like a chat or chatbot then create UI like real chat (ex. when user press enter on textbox then show message and give reponses or answers like real chatbot.) application for the user experience .
             - after visualizing the above all points then create components.
            
            ## Which step you have to follow for the create components :
            
            step 1 : `analyze` the provided Image
            step 2 : Create list of `components` which is you analyzed in the image
            step 3 : Take component one and generate the apropriate code and take steps visa versa for next component with logical actions which is need in component use DOM.
            step 4 : verify the image visual and your created code if you find the any loop hole so then go to the step 1 and re write the componnet code.
            
            return without any context or any explaination
            """
            
            """
            ***CONVERSATION***
             - if you get the convertational user input then give answer to the user with needed information without image. and give user to polite and informative answer with attractive designs with the help of HTML,CSS and JAVASCRIPT for users.
             
             - Give your all answer with the user experience design. with the help `animations`.
            """
        },
        {
            "role":"user",
            "content":[
                {"type":"text","text":prompt},
                # {"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{encoded_image}"}}
            ]
            # "content":f"{prompt} , this is data of image data:image/jpeg;base64,{encoded_image}"
        }
    ])
    
    # os.makedirs("output", exist_ok=True)

    with open("index.html", "w") as f:
        f.write(html.content)
    # with open("output/style.css", "w") as f:
        # f.write(html.css)
    # with open("output/script.js", "w") as f:
        # f.write(html.js)
    return {"data":html.content}


# generateHTML()
workflow = StateGraph(State)

workflow.add_node("generate",generateHTML)
workflow.set_entry_point("generate")
workflow.add_edge("generate",END)

graph = workflow.compile()
state = graph.invoke({"topic": "Who is the orange cap winner of IPL 2032 if not then predict.", "data": ""})
