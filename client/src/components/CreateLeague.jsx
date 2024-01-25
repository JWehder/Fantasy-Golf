import { useState } from "react";
import CreateLeagueStep1 from "./CreateLeagueStep1";
import CreateLeagueStep2 from "./CreateLeagueStep2";
import CreateLeagueStep3 from "./CreateLeagueStep3";

export default function CreateLeague() {
    const [createLeagueStep, setCreateLeagueStep] = useState(1)

    const createLeagueSteps = () => {
        if(createLeagueStep === 1) return <CreateLeagueStep1 setCreateLeagueStep={setCreateLeagueStep} />
        else if(createLeagueStep === 2) return <CreateLeagueStep2 setCreateLeagueStep={setCreateLeagueStep} />
        else if(createLeagueStep === 3)  return <CreateLeagueStep3 setCreateLeagueStep={setCreateLeagueStep} />
    }

    return (
        <div className="pt-20 pb-20">
            <p className="ml-96 pl-32 pb-4 text-2xl font-bold">Create A League</p>
            <div className="grid justify-items-center">
                {createLeagueSteps()}
            </div>
        </div>
    )
}