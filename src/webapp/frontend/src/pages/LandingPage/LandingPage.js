import React, { useState, useEffect } from 'react';

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

import HeaderSteps from '../../components/Steps2/Steps';
import SwipableCards from '../../components/SwipableCards/SwipableCards';

import CatalogPage from '../CatalogPage/CatalogPage';
import SearchPage from '../SearchPage/SearchPage';
import PersonalizationPage from '../PersonalizationPage/PersonalizationPage';


const { SubMenu } = Menu;
const { Header, Content, Footer, Sider } = Layout;

const Title = styled.div`
  font-size: 24px;
  color: black;
  text-align: left;
`;

const StyledSwipableCards = styled(SwipableCards)`
  background: red; // #f9fafb;
  // width: 300px;
  // height: 400px;
  // display: flex;
  // align-items: center;
  // justify-content: center;
  // flex-direction: column;
  // font-size: 150px;
  text-shadow: 0 10px 10px #d1d5db;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);
  border-radius: 50px;
  border: red;
  background-color: red !important;
`

function LogoIcon() {
  return (
    <span style={{fontSize: "40px"}}>
      🧥
    </span>
  )
}


function LandingPage() {
  const [collapsed, setCollapsed] = useState(false);
  const [selectedPage, setSelectedPage] = useState("catalog");

  useEffect(() => {}, [selectedPage]);

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider collapsible collapsed={collapsed} onCollapse={(c) => {setCollapsed(c)}}>
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
        <Menu theme="dark" defaultSelectedKeys={[selectedPage]} mode="inline">
          <Menu.Item key="catalog" icon={<AppstoreOutlined />} onClick={() => setSelectedPage("catalog")}>
            Product Catalog
          </Menu.Item>
          <Menu.Item key="search" icon={<SkinOutlined />} onClick={() => setSelectedPage("search")}>
            Search
          </Menu.Item>
          <Menu.Item key="personalize" icon={<FireOutlined />} onClick={() => setSelectedPage("personalize")}>
            Personalize
          </Menu.Item>
          <SubMenu key="sub1" icon={<UserOutlined />} title="User" onClick={() => setSelectedPage("explore")}>
            <Menu.Item key="3">Tom</Menu.Item>
            <Menu.Item key="4">Bill</Menu.Item>
            <Menu.Item key="5">Alex</Menu.Item>
          </SubMenu>
          <SubMenu key="sub2" icon={<TeamOutlined />} title="Team" onClick={() => setSelectedPage("explore")}>
            <Menu.Item key="6">Team 1</Menu.Item>
            <Menu.Item key="8">Team 2</Menu.Item>
          </SubMenu>
        </Menu>
      </Sider>
      <Layout className="site-layout">
        <Content style={{ margin: '16px 32px' }}>
          {(selectedPage === "catalog") && <CatalogPage />}
          {(selectedPage === "search") && <SearchPage />}
          {(selectedPage === "personalize") && <PersonalizationPage />}
        </Content>
        {false && (<Footer style={{ textAlign: 'center' }}>Ant Design ©2018 Created by Ant UED</Footer>)}
      </Layout>
    </Layout>
  )
}

export default LandingPage;
