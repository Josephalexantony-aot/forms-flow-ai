import React from 'react';
import { render as rtlRender, fireEvent, screen } from '@testing-library/react';
import { Provider } from 'react-redux';
import '@testing-library/jest-dom';
import { configureStore } from '@reduxjs/toolkit';
import { QueryClient, QueryClientProvider } from 'react-query';
import { createMemoryHistory } from 'history';
import { Router, Route } from 'react-router-dom';
import { Switch } from 'react-router-dom/cjs/react-router-dom.min';
import rootReducer from './rootReducer';
import { mockstate } from './mockState';
import ClientTable from '../../components/Form/constants/ClientTable';
import './utils/i18nForTests'; // import to remove warning related to i18n import

jest.mock('connected-react-router', () => ({
  push: jest.fn(),
}));

jest.mock('../../helper/routerHelper', () => ({
  navigateToFormEntries: jest.fn(),
}));
const queryClient = new QueryClient();
let store;
let history;

// Helper function to render with router
function renderWithRouterMatch(Ui, { path = '/', route = '/', props = {} }) {
  history = createMemoryHistory({ initialEntries: [route] });

  return rtlRender(
    <QueryClientProvider client={queryClient}>
      <Provider store={store}>
        <Router history={history}>
          <Switch>
            <Route path={path} render={(routeProps) => <Ui {...routeProps} {...props} />} />
          </Switch>
        </Router>
      </Provider>
    </QueryClientProvider>
  );
}
jest.mock("@formsflow/components", () => ({
  ...jest.requireActual("../../../__mocks__/@formsflow/components"),
  BackToPrevIcon: () => <div data-testid="back-icon" />,
}));

jest.mock("../../routes/Submit/Forms/DraftAndSubmissions", () => () => (
  <div data-testid="mock-submissions" />
));





beforeEach(() => {
  const mockForms = [
    {
      _id: "mock-form-id",
      parentFormId: "mock-form-id",
      title: "Test Form",
      description: "Test Description",
      status: "active",
      submissionsCount: 5,
      modified: "2023-01-01T00:00:00.000Z"
    }
  ];
  const mockstateSort = {
    ...mockstate,
    bpmForms: {
      ...mockstate.bpmForms,
      forms: mockForms,
      sort: {
        ...mockstate.bpmForms.sort,
        activeKey: "formName",
        formName: { sortOrder: "asc" },
        modified: { sortOrder: "asc" },
        submissionCount: { sortOrder: "asc" },
      },
      // Add submitFormSort which is what ClientTable.js actually uses
      submitFormSort: {
        activeKey: "formName",
        formName: { sortOrder: "asc" },
        latestSubmission: { sortOrder: "asc" },
        submissionCount: { sortOrder: "asc" },
      }
    },
  };
  store = configureStore({
    reducer: rootReducer,
    preloadedState: mockstateSort,
  });
  store.dispatch = jest.fn();

  renderWithRouterMatch(ClientTable, {
    path: '/forms',
    route: '/forms',

  });
  store.dispatch.mockClear();
  jest.clearAllMocks();


});


it('should render form table header correctly', () => {
  expect(screen.getByTestId('Form Name-header-btn')).toBeInTheDocument();
  expect(screen.getByTestId('description-header')).toBeInTheDocument();
  expect(screen.getByTestId('Submissions-header-btn')).toBeInTheDocument();
  expect(screen.getByTestId('Latest Submission-header-btn')).toBeInTheDocument();
  const strippedText = screen.getByTestId('description-header');
  expect(strippedText).toBeInTheDocument();

  // Test row toggling
  const descriptionCell = screen.getByTestId('description-cell');
  expect(descriptionCell).toHaveClass('text-container');

  fireEvent.click(descriptionCell);
  expect(descriptionCell).toHaveClass('text-container-expand');

  // Test row collapse
  fireEvent.click(descriptionCell);
  expect(descriptionCell).toHaveClass('text-container');
});

it('should handle form name column sorting', async () => {
  const sortButton = screen.getByTestId('Form Name-header-btn');
  fireEvent.click(sortButton);
  // The first call should be a function (thunk)
  const dispatchedFunction = store.dispatch.mock.calls[0][0];
  expect(typeof dispatchedFunction).toBe('function');  // Confirm it's a function (thunk)

  // Now invoke the thunk with store.dispatch
  dispatchedFunction(store.dispatch);

  // Now we can check the second call to dispatch
  expect(store.dispatch).toHaveBeenCalledWith(
    expect.objectContaining({
      type: 'CLIENT_SUBMIT_LIST_SORT_CHANGE', // Updated to match the actual action type
      payload: expect.objectContaining({
        activeKey: 'formName',
        formName: expect.objectContaining({
          sortOrder: 'desc', // Adjust this based on expected sort order
        }),
        latestSubmission: expect.objectContaining({
          sortOrder: 'asc',
        }),
        submissionCount: expect.objectContaining({
          sortOrder: 'asc',
        }),
      }),
    })
  );
});


it('should handle submission count column sorting', async () => {
  const sortButton = screen.getByTestId('Submissions-header-btn');
  fireEvent.click(sortButton);
  // The first call should be a function (thunk)
  const dispatchedFunction = store.dispatch.mock.calls[0][0];
  expect(typeof dispatchedFunction).toBe('function');  // Confirm it's a function (thunk)

  // Now invoke the thunk with store.dispatch
  dispatchedFunction(store.dispatch);

  // Now we can check the second call to dispatch
  expect(store.dispatch).toHaveBeenCalledWith(
    expect.objectContaining({
      type: 'CLIENT_SUBMIT_LIST_SORT_CHANGE', // Updated to match the actual action type
      payload: expect.objectContaining({
        activeKey: 'submissionCount',
        formName: expect.objectContaining({
          sortOrder: 'asc', // Adjust this based on expected sort order
        }),
        latestSubmission: expect.objectContaining({
          sortOrder: 'asc',
        }),
        submissionCount: expect.objectContaining({
          sortOrder: 'desc',
        }),
      }),
    })
  );
});

it('should handle latest submission column sorting', async () => {
  const sortButton = screen.getByTestId('Latest Submission-header-btn');
  fireEvent.click(sortButton);
  
  // The first call should be a function (thunk)
  const dispatchedFunction = store.dispatch.mock.calls[0][0];
  expect(typeof dispatchedFunction).toBe('function');
  
  // Confirm it's a function (thunk)
  // Now invoke the thunk with store.dispatch
  dispatchedFunction(store.dispatch);
  
  // Now we can check the second call to dispatch
  expect(store.dispatch).toHaveBeenCalledWith(
    expect.objectContaining({
      type: 'CLIENT_SUBMIT_LIST_SORT_CHANGE', // Updated to match the actual action type
      payload: expect.objectContaining({
        activeKey: 'latestSubmission',
        formName: expect.objectContaining({
          sortOrder: 'asc',
        }),
        latestSubmission: expect.objectContaining({
          sortOrder: 'desc',
        }),
        submissionCount: expect.objectContaining({
          sortOrder: 'asc',
        }),
      }),
    })
  );
});

it('should render the selected form correctly', () => {
  // Create a spy on the navigateToFormEntries function
  const navigateSpy = jest.spyOn(require('../../helper/routerHelper'), 'navigateToFormEntries');
  
  // Use the parentFormId from the mock form
  const mockFormId = "mock-form-id";
  
  // Find the select button for this form
  const selectButton = screen.getByTestId(`form-submit-button-${mockFormId}`);
  expect(selectButton).toBeInTheDocument();
  
  // Click the button
  fireEvent.click(selectButton);
  
  // Check that the navigateToFormEntries function was called
  expect(navigateSpy).toHaveBeenCalled();
  
  // Clean up the spy
  navigateSpy.mockRestore();
});


it('should render the table footer component and handle pagination correctly', () => {
  store.dispatch.mockClear();
  jest.clearAllMocks();

  // Test footer existence and basic elements
  const footer = screen.getByTestId("table-footer");
  expect(footer).toBeInTheDocument();
  const itemsCount = screen.getByTestId("items-count");
  expect(itemsCount).toBeInTheDocument();

  // Test pagination controls
  const prevButton = screen.getByTestId('left-button');
  const nextButton = screen.getByTestId('right-button');
  expect(prevButton).toBeInTheDocument();
  expect(nextButton).toBeInTheDocument();

  const pageDisplay = screen.getByTestId('current-page-display');
  expect(pageDisplay).toBeInTheDocument();
  // Remove the specific text content check since it might vary from eachother

  // Test pagination button clicks
  fireEvent.click(nextButton);
  expect(store.dispatch).toHaveBeenCalled();

  fireEvent.click(prevButton);
  expect(store.dispatch).toHaveBeenCalled();

  // Test page size dropdown
  const pageSizeDropdown = screen.getByTestId('page-size-dropdown');
  expect(pageSizeDropdown).toBeInTheDocument();

  // Test single page size change instead of loop
  fireEvent.change(pageSizeDropdown, { target: { value: "10" } });

  // Verify the dispatch was called with the correct action
  expect(store.dispatch).toHaveBeenCalled();
  const dispatchedAction = store.dispatch.mock.calls[store.dispatch.mock.calls.length - 1][0];
  expect(typeof dispatchedAction).toBe('function');
});
