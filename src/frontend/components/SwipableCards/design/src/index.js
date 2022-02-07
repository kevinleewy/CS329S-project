import React from "react"
import ReactDOM from "react-dom"
import { StreamlitProvider } from "streamlit-component-lib-react-hooks"
import SwipableCards from "./SwipableCards"
import "./styles.css"

ReactDOM.render(
  <React.StrictMode>
    <StreamlitProvider>
      <SwipableCards />
    </StreamlitProvider>
  </React.StrictMode>,
  document.getElementById("root")
)
