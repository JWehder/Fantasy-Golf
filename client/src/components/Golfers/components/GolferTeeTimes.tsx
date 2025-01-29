import React from "react"
import TableHeaders from "../../Utils/components/TableHeaders"
import GolferTeeTimesRows from "./GolflerTeeTimeRows"

export default function GolferTeeTimes() {
    const names = ["Mark", "Eduardo", "Justin"];
    const times = ["10:30", "1:30", "12:15"];
  
    // Generate 70 rows of random names and tee times
    const golfersAndTeeTimes = Array.from({ length: 70 }, () => ({
      golferName: names[Math.floor(Math.random() * names.length)],
      teeTime: times[Math.floor(Math.random() * times.length)],
    }));
  
    const handleGolferClick = (golferName: string) => {
      console.log(`Clicked on golfer: ${golferName}`);
    };
  
    return (
      <>
        <TableHeaders headers={["Name", "Tee Time"]} />
        {golfersAndTeeTimes.map((golferAndTeeTime, index) => (
          <GolferTeeTimesRows
            key={index} // Use a unique key for each row
            onClick={() => handleGolferClick(golferAndTeeTime.golferName)}
            golferName={golferAndTeeTime.golferName}
            teeTime={golferAndTeeTime.teeTime}
          />
        ))}
      </>
    );
};