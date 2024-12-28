import { useDispatch } from 'react-redux';
import { Tournament } from '../../../types/tournaments';
import Switch from '../../Utils/components/Switch';
import React, { useState } from 'react';
import { getLeaguesGolferDetails } from '../../Golfers/state/golferSlice';
import { AppDispatch, RootState } from '../../../store';
import { useParams } from 'react-router-dom';
import { resetLeaguesGolfersTournamentDetailsIds } from '../../Golfers/state/golferSlice';

export default function Tourney({ tournament } : { tournament: Tournament }) {

    const [checked, setChecked] = useState(false);
    const dispatch = useDispatch<AppDispatch>();

    // Call the useQuery hook, passing in tournament location and start date
    // const { data: weatherData, isLoading, error } = useFetchTournamentWeatherData(tournament)

    const { leagueId } = useParams<{ leagueId: string }>();

    // Use leagueId and dispatch action if it's defined
    function handleCheckedClick() {
        if (leagueId && checked === false) {
            setChecked(true);
            dispatch(getLeaguesGolferDetails({ tournamentId: tournament.id, leagueId }));
        }
        else if (checked === true) {
            setChecked(false);
            dispatch(resetLeaguesGolfersTournamentDetailsIds())
        } else {
            console.error("League ID is not available in URL parameters.");
        }
    }

    return (
        <div>
            <div className='flex-row h-16 w-11/12 mb-16 flex text-light font-PTSans'>
                <div className="flex-1 items-center pb-2">   
                    <h1 className='text-3xl font-bold'>
                        {tournament.Name}
                    </h1>
                    <div className="mt-2">
                        <p>
                            {tournament.StartDate} - {tournament.EndDate}
                        </p>
                        <p>
                            {tournament.Venue ? 
                            <>
                                <div>
                                    {tournament.Venue[0]}
                                </div>
                            </>
                            :
                            null
                            }
                        </p>
                        <p>Purse: {tournament.Purse}</p>
                    </div>
                </div>
                <div className="flex-1 text-right pb-2">
                {/* {isLoading ? (
                        <p>Loading weather...</p>
                    ) : error ? (
                        <p>Error loading weather</p>
                    ) : (
                        <>
                            <p>Temperature: {weatherData.temp}°F / {(weatherData.temp - 32) * 5/9}°C</p>
                            <p>Wind: {weatherData.windspeed} MPH / {weatherData.windgust} MPH Gusts</p>
                            <p>{weatherData.conditions}</p>
                            <p>Precipitation: {weatherData.precip}%</p>
                        </>
                )} */}
                </div>
            </div>
            <div className="p-4 text-center">
                <Switch checked={checked} setChecked={handleCheckedClick} />
            </div>
        </div>

    )
}