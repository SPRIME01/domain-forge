import React from "react";
import { BrowserRouter as Router, Route, Switch } from "react-router-dom";
import { MantineProvider } from "@mantine/core";
import { NotificationsProvider } from "@mantine/notifications";

import { HomePage } from "./pages/HomePage";
import { NotFoundPage } from "./pages/NotFoundPage";
import { EntityListPage } from "./pages/EntityListPage";
import { EntityDetailPage } from "./pages/EntityDetailPage";
import { EntityCreatePage } from "./pages/EntityCreatePage";
import { EntityEditPage } from "./pages/EntityEditPage";

const App: React.FC = () => {
  return (
    <MantineProvider withGlobalStyles withNormalizeCSS>
      <NotificationsProvider>
        <Router>
          <Switch>
            <Route exact path="/" component={HomePage} />
            <Route exact path="/entities" component={EntityListPage} />
            <Route exact path="/entities/new" component={EntityCreatePage} />
            <Route exact path="/entities/:id" component={EntityDetailPage} />
            <Route exact path="/entities/:id/edit" component={EntityEditPage} />
            <Route component={NotFoundPage} />
          </Switch>
        </Router>
      </NotificationsProvider>
    </MantineProvider>
  );
};

export default App;
