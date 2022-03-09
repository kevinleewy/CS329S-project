import React, { useState, useEffect } from 'react';
import axios from "axios";

import { Layout, Menu, Breadcrumb } from 'antd';
import Icon, {
  AppstoreOutlined,
  DesktopOutlined,
  FileOutlined,
  FireOutlined,
  HomeOutlined,
  PieChartOutlined,
  SkinOutlined,
  TeamOutlined,
  UserOutlined,
} from '@ant-design/icons';
import styled from "styled-components";

import "antd/dist/antd.css"
import './styles.css';

import SwipableCards from '../../components/SwipableCards/SwipableCards';

import NavigationPage from '../NavigationPage/NavigationPage';
import LandingPage from '../LandingPage/LandingPage';
import CatalogPage from '../CatalogPage/CatalogPage';
import SearchPage from '../SearchPage/SearchPage';
import PersonalizationPage from '../PersonalizationPage/PersonalizationPage';

import { AUTHENTICATE_TOKEN, GET_RECOMMENDATIONS, GUEST_ACCOUNT, SETUP } from '../../apiPaths';


const { SubMenu } = Menu;
const { Header, Content, Footer, Sider } = Layout;

const Title = styled.div`
  font-size: 24px;
  color: black;
  text-align: left;
`;

const StyledSwipableCards = styled(SwipableCards)`
  text-shadow: 0 10px 10px #d1d5db;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);
  border-radius: 50px;
`

function LogoIcon() {
  return (
    <span style={{fontSize: "40px"}}>
      🧥
    </span>
  )
}

const ACCEPTED_STATUS_CODE = 200;

function HomePage() {
  const [collapsed, setCollapsed] = useState(false);
  const [selectedPage, setSelectedPage] = useState("home");
  const [userId, setUserId] = useState(localStorage?.userId);
  const [setupDone, setSetupDone] = useState(false);

  useEffect(() => {
    if (!setupDone) {
      axios.post(SETUP, {})
      .then(function (response) {
        console.log(response);
        setTimeout(() => setSetupDone(!!userId), 6000);
        return response.data
      })
      .catch(function (error) {
        console.log(error);
      });
    }
  }, [userId]);

  useEffect(() => {}, [selectedPage]);
  
  useEffect(() => {
    const createGuestAccountOrUseToken = async () => {
      if (!userId) {
        const token = localStorage?.token;
        const username = localStorage?.username;
        if (!!token && !!username) {
          let config = {
            headers: {
              Authorization: "Token " + token,
            },
          };

          try {
            const token_response = await axios.post(
              AUTHENTICATE_TOKEN,
              { username },
              config
            );
            if (token_response.status === ACCEPTED_STATUS_CODE) {
              const loggedInUserId = token_response?.data?.userId;
              if (!!loggedInUserId) {
                setUserId(loggedInUserId);
              }
              return;
            } else {
              localStorage.removeItem("username");
              localStorage.removeItem("token");
            }
          } catch (error) {
            localStorage.removeItem("username");
            localStorage.removeItem("token");
          }
        }

        const result = await axios(GUEST_ACCOUNT);
        console.log(result);
        if (result.data && result.data.validated && result.data.id) {
          localStorage.setItem("userId", result.data.id)
          setUserId(result.data.id);
        }
      }
    };

    createGuestAccountOrUseToken();
  }, [userId]);

  console.log("userId:", userId);


  return !setupDone ? (<LandingPage />) : (
    <Layout hasSider style={{ minHeight: '100vh' }}>
      <Sider
        collapsible
        collapsed={collapsed}
        onCollapse={(c) => {setCollapsed(c)}}
        // style={{ 
        //   overflow: 'auto',
        //   height: '100vh',
        //   position: 'fixed',
        //   left: 0,
        //   top: 0,
        //   bottom: 0,
        // }}
      >
        {collapsed ? (
          <>
            <div className="logo" style={{ marginTop: "16px" }}>🧥</div>
          </>
        ) : (
          <div className="logo" style={{ transform: "scale(0.8)", marginTop: "16px", fontWeight: "bold" }}>
            🧥
            <span className="slow-visible" style={{fontSize: "35px", marginLeft: "5px", marginRight: "20px"}}>FashFlix</span>
          </div>
        )}
        <Menu theme="dark" selectedKeys={[selectedPage]} mode="inline">
          <Menu.Item key="home" icon={<HomeOutlined />} onClick={() => setSelectedPage("home")}>
            Home
          </Menu.Item>
          <Menu.Item key="catalog" icon={<AppstoreOutlined />} onClick={() => setSelectedPage("catalog")}>
            Product Catalog
          </Menu.Item>
          <Menu.Item key="personalize" icon={<FireOutlined />} onClick={() => setSelectedPage("personalize")}>
            Personalize
          </Menu.Item>
          <Menu.Item key="search" icon={<SkinOutlined />} onClick={() => setSelectedPage("search")}>
            Search
          </Menu.Item>
        </Menu>
      </Sider>
      <Layout style={{ /*marginLeft: 200*/ }} className="site-layout">
        <Content style={{ margin: '16px 32px' }}>
          {(selectedPage === "home") && <NavigationPage userId={userId} setSelectedPage={setSelectedPage} />}
          {(selectedPage === "catalog") && <CatalogPage userId={userId} />}
          {(selectedPage === "personalize") && <PersonalizationPage userId={userId} />}
          {(selectedPage === "search") && <SearchPage userId={userId} />}
        </Content>
        {false && (<Footer style={{ textAlign: 'center' }}>Ant Design ©2018 Created by Ant UED</Footer>)}
      </Layout>
    </Layout>
  )
}

export default HomePage;
