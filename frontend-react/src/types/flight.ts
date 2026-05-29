export interface FlightPayload {
  timestamp: number
  altitude: number
  speed: number
  ax: number
  ay: number
  az: number
  roll: number
  pitch: number
  yaw: number
  phase: string
  flight_id: string | null
  battery?: number
  latitude?: number
  longitude?: number
}

export type BufferKey =
  | 'altitude'
  | 'speed'
  | 'az'
  | 'roll'
  | 'pitch'
  | 'yaw'

export type ColumnId = 0 | 1 | 2 | 5 | 6 | 7 | 8 | 10 | 11 | 12
