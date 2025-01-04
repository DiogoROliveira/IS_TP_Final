import { NextRequest, NextResponse } from "next/server";

export async function POST(req: NextRequest) {
    const request_body  = await req.json()

    const city          = request_body?.search ?? ''

    const headers = {
        'content-type': 'application/json',
        'Cookie': `csrftoken=${process.env.CRSF_COOKIE}`,
        'X-CSRFToken': `${process.env.CRSF_COOKIE}`,
    }
    
    const requestBody = {
        query: `query Cities {
            cities${city.length > 0 ? `(nome: "${city}")` : ``} {
                nome
                latitude
                longitude
                id
            }
        }`
    }
    
    const options = {
        method: 'POST',
        headers,
        body: JSON.stringify(requestBody),
    }

    try{
        const promise = await fetch(`${process.env.GRAPHQL_API_BASE_URL}/graphql/`, options)

        if(!promise.ok){
            console.log(promise.statusText)
            return NextResponse.json({status: promise.status, message: promise.statusText}, { status: promise.status }) 
        }

        const data = await promise.json()

        return NextResponse.json(data) 
    }catch(e){
        console.log(e)
        return NextResponse.json({status: 500, message: e}, { status: 500  }) 
    }
}