// Reference: https://codesandbox.io/s/tinder-style-swipe-framer-motion-cq3f6
// import { Streamlit, withStreamlitConnection } from "streamlit-component-lib"
// import { useRenderData } from "streamlit-component-lib-react-hooks"
import React, { useEffect, useState } from "react"
import styled from "styled-components"

import { CardStack } from "./CardStack"

const CardStackWrapper = styled(CardStack)`
  // background: #1f2937;
  // background: #f9fafb;
  height: 100%;

  // box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);
  // border-radius: 8px;
`

const CardItem = styled.div`
  background: #f9fafb;
  width: 300px;
  height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  font-size: 150px;
  text-shadow: 0 10px 10px #d1d5db;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);
  border-radius: 8px;
  
  transform: ${() => {
    let rotation = Math.random() * (5 - -5) + -5
    return `rotate(${rotation}deg)`
  }};
  
  overflow: hidden;
  pointer-events: none;

  -webkit-touch-callout: none; /* iOS Safari */
    -webkit-user-select: none; /* Safari */
     -khtml-user-select: none; /* Konqueror HTML */
       -moz-user-select: none; /* Old versions of Firefox */
        -ms-user-select: none; /* Internet Explorer/Edge */
            user-select: none; /* Non-prefixed version, currently
                                  supported by Chrome, Edge, Opera and Firefox */
`

const CardImage = styled.img`
  position: absolute;
  height: 100%;
  pointer-events: none;
`

export const SwipableCards = ({img_uris}) => {
  // Streamlit.setFrameHeight(500)

  // const renderData = useRenderData()

  const [imgs, setImgs] = useState(img_uris || [])
  const [isFocused, setIsFocused] = useState(false)

  const onVote = (item, vote) => {
    console.log(item.props, vote);
    // Streamlit.setComponentValue(vote);
  }

  // console.log("props:", props)
  // const imgs = props.imgs || [] //renderData.args["imgs"]
  // console.log("imgs:", imgs)
  const last_card_emoji = "🙈" //renderData.args["last_card_emoji"] || "🙈"

  useEffect(() => {
    // Update the document title using the browser API
    document.title = `${imgs.lengths} images`;
  });

  // const theme = renderData.theme
  // const style = {}
  // if (theme) {
  //   const borderStyling = `1px solid ${isFocused ? theme.primaryColor : "gray"}`
  //   style.border = borderStyling
  //   style.outline = borderStyling
  // }

  return (
    <div id="SwipableCards" style={{ height: "500px" }}>
      <CardStackWrapper onVote={onVote}>
        <CardItem data-value="pancakes" disabled>
          {last_card_emoji}
          <div style={{ fontSize: "25px", color: "black" }}>
            That's all for now!
          </div>
        </CardItem>
        {imgs.map((img, index) => {
          return (
            <CardItem data-value="waffles" whileTap={{ scale: 1.15 }}>
              <CardImage src={img} width="100%" height="100%" />
            </CardItem>
          )
        })}
      </CardStackWrapper>
    </div>
  )
}

export default SwipableCards
