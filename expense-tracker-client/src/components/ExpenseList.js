import React from 'react';

function ExpenseList({ expenses, onSelectExpense, selectedExpense }) {
  return (
    <div>
      <h2>Expenses</h2>
      <ul>
        {expenses.map(expense => (
          <li
            key={expense.id}
            onClick={() => onSelectExpense(expense)}
            style={{
              cursor: 'pointer',
              backgroundColor: selectedExpense && selectedExpense.id === expense.id ? '#f0f0f0' : 'transparent'
            }}
          >
            {expense.id} - {expense.name}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default ExpenseList;
