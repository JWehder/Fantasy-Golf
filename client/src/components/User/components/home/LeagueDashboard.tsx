import React from 'react';
import Standings from './Standings';
import Roster from './Roster';
import { useState } from 'react';
import Leaderboard from './Leaderboard';
import Golfers from '../../../Golfers/components/Golfers';
import SquigglyUnderline from "../../../Utils/components/SquigglyLine"
import Schedule from './Schedule';
import { useDispatch, useSelector } from 'react-redux';
import { useParams } from 'react-router-dom';
import Button from '../../../Utils/components/Button';
import BackButton from '../../../Utils/components/BackButton';
import NextButton from '../../../Utils/components/NextButton';
import { RootState } from '../../../../store';
import Modal from '../../../Utils/components/Modal';
import { unsetSelectedGolfer } from '../../../Golfers/state/golferSlice';
import { useQueryClient } from '@tanstack/react-query';
import PlayerPage from '../../../Golfers/components/player/PlayerPage';

export default function LeagueDashboard() {
    const dispatch = useDispatch();
    const { leagueId } = useParams();
    const queryClient = useQueryClient();

    const [activeComponent, setActiveComponent] = useState("Schedule");

    const signedIn = useSelector((state: RootState) => state.users.user);
    const selectedGolfer = useSelector((state: RootState) => state.golfers.selectedGolfer);

    // code to be implemented when we have data

    const onClose = () => {
        dispatch(unsetSelectedGolfer());
        queryClient.invalidateQueries({ queryKey: ['golferTournamentDetails'] });
    };

    console.log(leagueId);

    return (
        <>
            <div className='flex-row h-16 w-11/12 mb-5 flex items-center text-light font-PTSans pt-3 min-w-[750px]'>

                <div className='flex flex-col w-1/3'>
                    <div className='flex justify-center items-center flex-row'>
                        <h1 className='text-xl lg:text-4xl md:text-2xl sm:text-xl'>
                            League Name
                        </h1>
                    </div>

                    <div className='flex justify-center items-center flex-row'>
                        <BackButton 
                        size="4" 
                        color={"stroke-light"} 
                        handleBackClick={() => console.log("Clicked me")}
                        />
                        <NextButton 
                        size="4" 
                        color={"stroke-light"} 
                        handleNextClick={() => console.log("Clicked me")}
                        />
                    </div>
                </div>

                <div className='p-5 flex items-center justify-center w-1/3'>
                        <SquigglyUnderline 
                        items={[{name:"Schedule"}, {name: "Standings"}, {name:"Team"}, {name:"Leaderboard"}, {name:"Golfers"}]}
                        setActiveComponent={setActiveComponent}
                        active={activeComponent}
                        />
                </div>

                <div className='w-1/3 flex justify-center items-center'>
                    <Button
                    variant="secondary"
                    type="null"
                    disabled={false}
                    size="md"
                    onClick={() => console.log("Clicked me")}
                    >
                        Settings
                    </Button>
                </div>

            </div>
            <div className='w-10/12 bg-middle rounded-lg overflow-auto min-w-[500px] min-h-[400px] h-[350px] py-3 flex-grow shrink'> 

                { activeComponent === "Standings" && 
                    <div className='flex items-center justify-center'>
                        <Standings />
                    </div>
                }
                { activeComponent === "Team" && 
                    <div className='flex items-center justify-center'>
                        <Roster />
                    </div>
                } 
                { activeComponent === "Leaderboard" && 
                    <div className='flex items-center justify-center'>
                        <Leaderboard />
                    </div>
                }
                { activeComponent === "Golfers" && 
                    <div className='flex items-center justify-center'>
                        <Golfers />
                    </div>
                }
                { activeComponent === "Schedule" && 
                    <div className='flex items-center justify-center'>
                        <Schedule />
                    </div>
                }
                { selectedGolfer ?
                    <Modal 
                    open={open} 
                    onClose={onClose} 
                    bgColor="dark-green"
                    closeButtonColor={'light'}
                    >
                    <div className="w-full h-auto flex items-center justify-center">
                        <div className="w-[90%] p-4 bg-middle rounded-xl transition-all duration-300 ease-in-out">
                            <PlayerPage />
                        </div>
                    </div>
                    </Modal>
                    :
                    ""
                }
            </div>

        </>
    );
  }