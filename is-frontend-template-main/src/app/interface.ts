export interface City{
    nome: string
    latitude: number
    longitude: number
    id: number
}

export interface Cities{
    cities: City[]
}

export interface GraphQlCities{
    data: Cities
}