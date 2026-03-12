import mammoth from "mammoth"
import {cleanLines} from "./cleaner.js"

export async function parseDocx(filePath){

const result=await mammoth.extractRawText({path:filePath})

const lines=cleanLines(result.value)

let data=[]

let currentQuestion=null
let options={}

for(let i=0;i<lines.length;i++){

const line=lines[i]

if(/^\d+\./.test(line)){

currentQuestion=lines[i+1]
options={}

continue

}

if(/^[A-D]\)/.test(line)){

const key=line[0]

const optionText=lines[i+1]

const status=lines[i+2]

options[key]={
text:optionText,
correct:status==="Дуруст"
}

}

if(Object.keys(options).length===4){

for(const k in options){

if(options[k].correct){

data.push({

question:currentQuestion,
answer:options[k].text

})

}

}

options={}

}

}

return data

}