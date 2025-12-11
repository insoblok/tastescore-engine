export interface IApiResponse {
	status_code?: number;
	data?: {
		histories: string;
		summary?: string;
    transactions?:string;
	};
	statusText?: string;
}

export interface ILocationState {
  network: number
  wallet: string
}