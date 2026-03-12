export function cleanLines(text){

const trashWords=[
"Факултет",
"Кафедра",
"Фан",
"窗体顶端",
"窗体底端",
"Тести оддӣ"
]

let lines=text
.split("\n")
.map(x=>x.trim())
.filter(x=>x.length>0)

lines=lines.filter(line=>{

for(const t of trashWords){

if(line.includes(t)) return false

}

return true

})

return lines

}