
import LeafleatMap from "./components/MainMap";
import Sidebar from "./components/MainSideBar";
import { GraphQlCities } from "./interface";

const getMapaData = async(search: string) => {
  "use server"

  const headers = {
    'content-type': 'application/json',
    'Cookie': `crsftoken=${process.env.CRSF_COOKIE}`,
    'X-CSRFToken': `${process.env.CRSF_COOKIE}`,
  }

  const options = {
    method: 'POST',
    headers,
    body: JSON.stringify({
      search: search
    })
  }

  const response = await fetch(`${process.env.NEXT_PUBLIC_URL}/api/cities`, options)

  return await response.json()
}

const updatePoint = async(id: number, latitude: number, longitude: number) => {
  "use server"

  const headers = {
    'content-type': 'application/json',
    'Cookie': `csrftoken=${process.env.CRSF_COOKIE}`,
    'X-CSRFToken': `${process.env.CRSF_COOKIE}`,
  }

  const options = {
    method: 'PUT',
    headers,
    body: JSON.stringify({
      latitude: latitude,
      longitude: longitude
    })
  }

  const response = await fetch(`${process.env.NEXT_PUBLIC_URL}/api/cities/${id}`, options)

  return await response.json()
}

export default async function Home({ searchParams }: {searchParams : any}) {
  const params: any = await searchParams

  const search: string = params?.search ?? ''

  const mapa_data: GraphQlCities = await getMapaData(search)

  return (
    <div className="h-[100vh] w-full">
      <nav className="w-[250px] h-full absolute left-0">
        <Sidebar searchValue={search} />
      </nav>
      <main className="h-full" style={{ marginLeft: 250}}>
        <LeafleatMap cities={mapa_data.data.cities} updatePoint={updatePoint} />
      </main>
    </div>
  );
}
