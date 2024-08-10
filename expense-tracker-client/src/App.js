import React, { useState, useEffect } from 'react';
import axios from 'axios';
import ExpenseList from './components/ExpenseList';
import ExpenseForm from './components/ExpenseForm';
import ExpenseDetails from './components/ExpenseDetails';

const BASE_URL = "http://127.0.0.1:8000";

function App() {
  const [expenses, setExpenses] = useState([]);
  const [selectedExpense, setSelectedExpense] = useState(null);

  useEffect(() => {
    loadExpenses();
  }, []);

  const loadExpenses = async () => {
    try {
      const response = await axios.get(`${BASE_URL}/expenses/all`);
      setExpenses(response.data);
    } catch (error) {
      console.error("Failed to load expenses", error);
    }
  };

  const addExpense = async (expense) => {
    try {
      await axios.post(`${BASE_URL}/expenses/`, expense);
      loadExpenses();
    } catch (error) {
      console.error("Failed to add expense", error);
    }
  };

  const updateExpense = async (expense) => {
    try {
      await axios.put(`${BASE_URL}/expenses/${expense.id}`, expense);
      loadExpenses();
      setSelectedExpense(null);
    } catch (error) {
      console.error("Failed to update expense", error);
    }
  };

  const deleteExpense = async (id) => {
    try {
      await axios.delete(`${BASE_URL}/expenses/${id}`);
      loadExpenses();
      setSelectedExpense(null);
    } catch (error) {
      console.error("Failed to delete expense", error);
    }
  };

  return (
    <div className="App">
      <h1>Expense Tracker</h1>
      <ExpenseForm onSubmit={addExpense} clearForm={() => setSelectedExpense(null)} />
      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
        <div style={{ flex: 1, marginRight: '20px' }}>
          <ExpenseList expenses={expenses} onSelectExpense={setSelectedExpense} selectedExpense={selectedExpense} />
        </div>
        <div style={{ flex: 1, marginLeft: '20px' }}>
          {selectedExpense && (
            <>
              <ExpenseDetails
                expense={selectedExpense}
                onDelete={deleteExpense}
              />
              <ExpenseForm
                onSubmit={updateExpense}
                expense={selectedExpense}
                clearForm={() => setSelectedExpense(null)}
              />
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
