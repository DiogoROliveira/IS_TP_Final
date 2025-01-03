import type { NextApiRequest, NextApiResponse } from 'next'
import { NextRequest, NextResponse } from 'next/server'
 
export async function PUT(req: NextRequest) {
    const request_body  = await req.json()
    const id            = req.nextUrl.pathname.split("/")[3]

    const headers = {
        'content-type': 'application/json',
        'Cookie': `csrftoken=${process.env.CRSF_COOKIE}`,
        'X-CSRFToken': `${process.env.CRSF_COOKIE}`,
    }
    
    const requestBody = {
        query: `mutation UpdateCity {
            updateCity(id: "${id}", latitude: "${request_body.latitude}", longitude: "${request_body.longitude}") {
                city {
                    id
                    nome
                    latitude
                    longitude
                }
            }
        }`
    }
    
    const options = {
        method: 'POST',
        headers,
        body: JSON.stringify(requestBody),
    }

    try{
        const promise = await fetch(`${process.env.GRAPHQL_API_BASE_URL}/graphql/cities/`, options)

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
