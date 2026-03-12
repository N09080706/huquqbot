import mammoth from "mammoth"
import { cleanLines } from "./cleaner.js"

export async function parseDocx(filePath) {

const result = await mammoth.extractRawText({ path: filePath })

const lines = cleanLines(result.value)

let data = []

let question = null
let option = null

for (let i = 0; i < lines.length; i++) {

const line = lines[i]

// обнаружение вопроса
if (/^\d+\s*[.)]/.test(line)) {

question = lines[i + 1]

continue
}

// вариант ответа
if (/^[A-D][.)]/.test(line)) {

option = lines[i + 1]

}

// правильный ответ
if (line === "Дуруст" && question && option) {

data.push({
question: question,
answer: option
})

}

}

return data

}
