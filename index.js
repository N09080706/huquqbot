import TelegramBot from "node-telegram-bot-api"
import axios from "axios"
import fs from "fs-extra"
import {parseDocx} from "./parser.js"

const bot=new TelegramBot(process.env.BOT_TOKEN,{polling:true})

bot.onText(/\/start/,msg=>{

bot.sendMessage(msg.chat.id,
"📄 Отправь DOCX файл с тестами\n\nЯ превращу его в JSON")

})

bot.on("document",async msg=>{

const chatId=msg.chat.id

const fileId=msg.document.file_id

const file=await bot.getFile(fileId)

const url=`https://api.telegram.org/file/bot${process.env.BOT_TOKEN}/${file.file_path}`

await fs.ensureDir("downloads")
await fs.ensureDir("outputs")

const docxPath=`downloads/${fileId}.docx`
const jsonPath=`outputs/${fileId}.json`

const response=await axios({
url,
method:"GET",
responseType:"stream"
})

const writer=fs.createWriteStream(docxPath)

response.data.pipe(writer)

writer.on("finish",async()=>{

const data=await parseDocx(docxPath)

const json=`const data = ${JSON.stringify(data,null,2)}`

await fs.writeFile(jsonPath,json)

await bot.sendDocument(chatId,jsonPath)

})

})