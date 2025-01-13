import { NextRequest, NextResponse } from "next/server";

export async function POST(req: NextRequest) {
    const request_body  = await req.json();
    const expression    = request_body?.expression ?? '';
    const ascending     = request_body?.ascending ?? true;

    console.log(expression, ascending);

    const requestOptions = {
        method: "POST",
        body: JSON.stringify({
            "file_name":    "tiny.xml",
            "order_by_xpath":  `.//${expression}`,
            "ascending":    `${ascending}`
        }),
        headers: {
            'content-type': 'application/json'
        }
    };

    try {
        const response = await fetch(`${process.env.REST_API_BASE_URL}/api/xml/order-by`, requestOptions);

        if (!response.ok) {
            console.log(response.statusText);
            return NextResponse.json({ status: response.status, message: response.statusText }, { status: response.status });
        }

        const responseText = await response.text();

        const parsedResponse = JSON.parse(responseText);
        const rawXml = parsedResponse.result;

        const xmlWithRoot = `<root>${rawXml}</root>`;

        const formattedXml = formatXml(xmlWithRoot);

        return new Response(formattedXml, {
            headers: { "Content-Type": "application/xml" }
        });
    } catch (e) {
        console.log(e);
        return NextResponse.json({ status: 500, message: e }, { status: 500 });
    }
}

function formatXml(xml: string): string {
    const PADDING = "  ";
    const reg = /(>)(<)(\/*)/g;
    let formatted = xml.replace(reg, "$1\n$2$3");
    let pad = 0;
    const lines = formatted.split("\n");

    return lines.map((line) => {
        if (line.match(/<\/\w+>/)) pad = Math.max(pad - 1, 0);
        const indent = PADDING.repeat(pad);
        if (line.match(/<[^!\?].*>/)) pad += 1;
        return indent + line;
    }).join("\n");
}
