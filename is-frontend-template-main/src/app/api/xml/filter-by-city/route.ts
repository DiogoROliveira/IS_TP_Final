import { NextRequest, NextResponse } from "next/server";

export async function POST(req: NextRequest) {
    const request_body  = await req.json()

    const city          = request_body?.city ?? ''

    const requestOptions = {
        method: "POST",
        body: JSON.stringify({
            "file_name":    "latitude e longitude das cidades.xml",
            "xpath_query":  `//city[contains(nome, '${city}')]`
        }),
        headers: {
            'content-type': 'application/json'
        }
    }

    try{
        const promise = await fetch(`${process.env.REST_API_BASE_URL}/api/xml/filter-by/`, requestOptions)

        if(!promise.ok){
            console.log(promise.statusText)
            return NextResponse.json({status: promise.status, message: promise.statusText}, { status: promise.status }) 
        }

        return new Response(await promise.text(), { headers: { "Content-Type": "text/xml" } });
    }catch(e){
        console.log(e)

        return NextResponse.json({status: 500, message: e}, { status: 500  }) 
    }
}
