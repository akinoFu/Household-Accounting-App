import React, { useEffect, useState } from 'react'
import '../App.css';

export default function HealthCheck() {
    const [isLoaded, setIsLoaded] = useState(false);
    const [stats, setStats] = useState({});
    const [error, setError] = useState(null)

	const getStats = () => {
	
        fetch(`http://acit3855-household-account-app.eastus.cloudapp.azure.com/health/health`)
            .then(res => res.json())
            .then((result)=>{
				console.log("Received Health Check")
                setStats(result);
                setIsLoaded(true);
            },(error) =>{
                setError(error)
                setIsLoaded(true);
            })
    }
    useEffect(() => {
		const interval = setInterval(() => getStats(), 2000); // Update every 2 seconds
		return() => clearInterval(interval);
    }, [getStats]);

    if (error){
        return (<div className={"error"}>Error found when fetching from API</div>)
    } else if (isLoaded === false){
        return(<div>Loading...</div>)
    } else if (isLoaded === true){
        return(
            <div>
                <h1>Health Check</h1>
                <table className={"StatsTable"}>
					<tbody>
						<tr>
							<th>Receiver:</th>
							<td>{stats['receiver']}</td>
						</tr>
						<tr>
                            <th>Storage:</th>
							<td>{stats['receiver']}</td>
						</tr>
						<tr>
                            <th>Processing:</th>
							<td>{stats['receiver']}</td>
						</tr>
						<tr>
                            <th>Audit:</th>
							<td>{stats['receiver']}</td>
						</tr>
                        <tr>
                            <th>Last Update:</th>
							<td>{stats['last_update']}</td>
						</tr>
						{/* <tr>
							<td colspan="2">Max HR: {stats['max_bp_sys_reading']}</td>
						</tr> */}
					</tbody>
                </table>


            </div>
        )
    }
}
