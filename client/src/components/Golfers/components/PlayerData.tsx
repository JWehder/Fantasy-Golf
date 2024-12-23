import Avatar  from "../../Utils/components/Avatar";
import React from "react";
import { Golfer } from "../../../types/golfers";
import TData from "../../Utils/components/TData";

interface PlayerDataProps {
    player: Golfer;
    even: Boolean;
    onClick?: () => void; // Add onClick as an optional prop
}

export default function PlayerData({ 
    player,
    even,
    onClick
}: PlayerDataProps) {

    const brightness = even ? 'brightness-125' : '';
    const space = even ? 'my-2' : '';

    const desiredKeys: (keyof Golfer)[]= ["AvgScore", "Top10s", "Wins", "Cuts", "FedexPts"]

    return (
        <div 
        className={`w-full flex bg-middle h-auto justify-center items-center 
        cursor-pointer hover:shadow-lg shadow-middle flex-row 
        border-box ${brightness} text-sm md:text-sm lg:text-md sm:text-sm 
        truncate hover:border-1 ${space} overflow-visible rounded-lg transition-all group/team p-2`}
        onClick={onClick}
        >
            <div className="text-center flex w-1/2 items-center">
                <div className="w-1/6">
                    {player.Rank}
                </div>
                <div className="w-5/6 text-left flex items-center pl-6 group-hover/team:translate-x-2 transition duration-200">
                    <div className="flex-1 flex">
                        <div className="flex-col">
                            <Avatar 
                            imgUrl={""}
                            name={`${player.FirstName } ${player.LastName}`}
                            size={"10"}
                            />
                        </div>

                        <div className="pl-3 flex-col flex justify-center">
                            <div>
                                {`${player.FirstName } ${player.LastName}`} {player.Flag ? player.Flag : null}
                            </div>
                            <span>
                                {player.Country ? player.Country : null} Age: {player.Age}
                            </span>
                        </div>
                    </div>
                </div>
            </div>
            <div className="w-1/2 flex flex-row items-center space-x-5">
                {
                    desiredKeys.map((data, idx) => {
                        return (
                            <TData 
                            key={`${data}-${idx}`}
                            >
                                {player[data]}
                            </TData>
                        )
                    })
                }
            </div>
        </div>
    )
}