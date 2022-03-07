import React from 'react';

import styled from "styled-components";

import "antd/dist/antd.css"
import './styles.css';


const Container = styled.div`
  & {
    height: 100vh;
    width: 100vw;
    background: white; /*#f1f1f1;*/
    background-size: cover;
    display:flex;
    flex-direction:column;
    justify-content:center;
    align-items:center;
  }
`

const ACCEPTED_STATUS_CODE = 200;

function LandingPage() {
  return (
    <Container className="inner">
      <div className="title" style={{zIndex: 100}}>
        🧥 FashFlix
        <div style={{fontSize: "30px", marginTop: "-20px"}}>Less Scrolling • More Possibilities • Better Outfits</div>
      </div>
      <div
        className="bottom-left"
        style={{
          height:"300px",
          width:"300px",
          borderRadius: "50%",
          zIndex: 50,
          background: "url('https://c.tenor.com/A6iXJhqsqU0AAAAC/shoes-shopping.gif')",
          backgroundSize: "cover",
        }}
      />
      <div
        className="top-right"
        style={{height:"400px", width:"400px", borderRadius: "50%", zIndex: 50}}
      />
      <img
        className="bottom"
        style={{width:"90%"}}
        src="https://static.vecteezy.com/system/resources/previews/004/113/684/original/shopping-concept-for-web-banner-woman-buys-online-shopper-makes-purchases-and-receives-online-orders-at-store-modern-people-scene-illustration-in-flat-cartoon-design-with-person-characters-vector.jpg"
      />
    </Container>
  )
}

export default LandingPage;
