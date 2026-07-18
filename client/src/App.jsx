import { BrowserRouter, Routes, Route } from "react-router-dom";

import Home from "./pages/Home";
import PersonaSelect from "./pages/PersonaSelect";
import ScenarioSelect from "./pages/ScenarioSelect";
import DifficultySelect from "./pages/DifficultySelect";
import Chat from "./pages/Chat";
import Debrief from "./pages/Debrief";

function App(){

    return(

        <BrowserRouter>

            <Routes>

                <Route path="/" element={<Home/>}/>

                <Route path="/persona" element={<PersonaSelect/>}/>

                <Route path="/scenario" element={<ScenarioSelect/>}/>

                <Route path="/difficulty" element={<DifficultySelect/>}/>

                <Route path="/chat" element={<Chat/>}/>

                <Route path="/debrief" element={<Debrief/>}/>

            </Routes>

        </BrowserRouter>

    );

}

export default App;