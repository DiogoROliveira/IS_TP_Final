import { NextRequest, NextResponse } from "next/server";

export async function POST(req: NextRequest) {
    const formData      = await req.formData()
    const body          = Object.fromEntries(formData)
    const file          = (body.file as Blob) || null
    const dtd_file      = (body.dtd_file as Blob) || null

    if(!file || !dtd_file){
        return NextResponse.json({status: 500, message: 'Files not sent!'}, { status: 500  }) 
    }

    const formdata      = new FormData()

    formdata.append("file", file)
    formdata.append("file_dtd", dtd_file)

    const requestOptions = {
        method: "POST",
        body: formdata
    }

    try{
        const promise = await fetch(`${process.env.REST_API_BASE_URL}/api/upload-file/by-chunks`, requestOptions)

        if(!promise.ok){
            return NextResponse.json({status: promise.status, message: promise.statusText}, { status: promise.status }) 
        }

        return NextResponse.json(await promise.json()) 
    }catch(e){
        return NextResponse.json({status: 500, message: e}, { status: 500  }) 
    }
}
