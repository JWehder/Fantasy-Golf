import React from "react"
import TableHeaders from "../../Utils/components/TableHeaders"
import GolferTeeTimesRows from "./GolflerTeeTimeRows"
import { GolferTournamentDetails } from "../../../types/golferTournamentDetails"
import THead from "../../Utils/components/THead"

export default function GolferTeeTimes(
  {
  golfers,
  currentRoundNum
  }
  :
  {
  golfers: GolferTournamentDetails[]
  currentRoundNum: string
  }

) {
  
    const handleGolferClick = (golferName: string) => {
      console.log(`Clicked on golfer: ${golferName}`);
    };

    return (
      <>
        <div className="w-full flex bg-middle text-xs truncate font-bold p-2 items-center text-clip border-b border-light">
            <div className="flex w-1/2 flex-row bg-middle">
                <THead 
                  datapoint={"golfer name"}
                />
            </div>
            <div className="flex w-1/2 flex-row bg-middle">
                <THead 
                  datapoint={"tee time"}
                />
            </div>

        </div>
        {golfers.map((golfer, index) => (
          <GolferTeeTimesRows
            key={index} // Use a unique key for each row
            onClick={() => handleGolferClick(golfer.Name)}
            even={index % 2 == 0}
            golferName={golfer.Name}
            teeTime={golfer.TeeTimes[currentRoundNum]}
          />
        ))}
      </>
    );
};