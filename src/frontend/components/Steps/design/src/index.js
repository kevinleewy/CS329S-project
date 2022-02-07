import React from "react"
import ReactDOM from "react-dom"
import { StreamlitProvider } from "streamlit-component-lib-react-hooks"
import HeaderSteps from "./Steps"

ReactDOM.render(
  <React.StrictMode>
    <StreamlitProvider>
      <HeaderSteps />
    </StreamlitProvider>
  </React.StrictMode>,
  document.getElementById("root")
)
