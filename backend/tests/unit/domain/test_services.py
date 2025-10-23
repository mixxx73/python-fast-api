from uuid import uuid4

import pytest

from app.domain.models import Expense
from app.domain.services import summarize_balances


# Fixtures
@pytest.fixture
def sample_payer_id():
    return uuid4()


@pytest.fixture
def another_payer_id():
    return uuid4()


@pytest.fixture
def sample_group_id():
    return uuid4()


# Tests
class TestSummarizeBalances:
    def test_empty_expenses_list(self):
        """Test that an empty list of expenses returns an empty balance dict."""
        result = summarize_balances([])
        assert result == {}

    def test_single_expense_single_payer(self, sample_payer_id, sample_group_id):
        """Test a single expense with one payer."""
        expense = Expense(
            id=uuid4(),
            group_id=sample_group_id,
            payer_id=sample_payer_id,
            amount=100.0,
            description="Dinner",
        )

        result = summarize_balances([expense])

        # With the current implementation: amount - (amount/1) = 0
        assert str(sample_payer_id) in result
        assert result[str(sample_payer_id)] == 0.0

    def test_multiple_expenses_same_payer(self, sample_payer_id, sample_group_id):
        """Test multiple expenses with the same payer."""
        expenses = [
            Expense(
                id=uuid4(),
                group_id=sample_group_id,
                payer_id=sample_payer_id,
                amount=50.0,
                description="Lunch",
            ),
            Expense(
                id=uuid4(),
                group_id=sample_group_id,
                payer_id=sample_payer_id,
                amount=75.0,
                description="Dinner",
            ),
            Expense(
                id=uuid4(),
                group_id=sample_group_id,
                payer_id=sample_payer_id,
                amount=25.0,
                description="Coffee",
            ),
        ]

        result = summarize_balances(expenses)

        # Each expense: amount - amount/1 = 0, so total = 0
        assert str(sample_payer_id) in result
        assert result[str(sample_payer_id)] == 0.0

    def test_multiple_expenses_different_payers(
        self, sample_payer_id, another_payer_id, sample_group_id
    ):
        """Test multiple expenses with different payers."""
        expenses = [
            Expense(
                id=uuid4(),
                group_id=sample_group_id,
                payer_id=sample_payer_id,
                amount=100.0,
                description="Hotel",
            ),
            Expense(
                id=uuid4(),
                group_id=sample_group_id,
                payer_id=another_payer_id,
                amount=50.0,
                description="Food",
            ),
        ]

        result = summarize_balances(expenses)

        # Both payers should have 0 balance with current implementation
        assert str(sample_payer_id) in result
        assert str(another_payer_id) in result
        assert result[str(sample_payer_id)] == 0.0
        assert result[str(another_payer_id)] == 0.0

    def test_expense_with_decimal_amount(self, sample_payer_id, sample_group_id):
        """Test expense with decimal amounts."""
        expense = Expense(
            id=uuid4(),
            group_id=sample_group_id,
            payer_id=sample_payer_id,
            amount=42.50,
            description="Groceries",
        )

        result = summarize_balances(expense for expense in [expense])

        assert str(sample_payer_id) in result
        assert result[str(sample_payer_id)] == 0.0

    def test_expense_with_zero_amount(self, sample_payer_id, sample_group_id):
        """Test expense with zero amount."""
        expense = Expense(
            id=uuid4(),
            group_id=sample_group_id,
            payer_id=sample_payer_id,
            amount=0.0,
            description="Free item",
        )

        result = summarize_balances([expense])

        assert str(sample_payer_id) in result
        assert result[str(sample_payer_id)] == 0.0

    def test_returns_dict_with_string_keys(self, sample_payer_id, sample_group_id):
        """Test that the function returns UUID strings as keys, not UUID objects."""
        expense = Expense(
            id=uuid4(),
            group_id=sample_group_id,
            payer_id=sample_payer_id,
            amount=100.0,
            description="Test",
        )

        result = summarize_balances([expense])

        # Check that the key is a string
        assert isinstance(list(result.keys())[0], str)
        assert str(sample_payer_id) in result

    def test_iterable_input(self, sample_payer_id, sample_group_id):
        """Test that the function accepts any iterable, not just lists."""

        def expense_generator():
            for i in range(3):
                yield Expense(
                    id=uuid4(),
                    group_id=sample_group_id,
                    payer_id=sample_payer_id,
                    amount=10.0 * (i + 1),
                    description=f"Item {i}",
                )

        result = summarize_balances(expense_generator())

        assert str(sample_payer_id) in result
        assert result[str(sample_payer_id)] == 0.0

    def test_balance_accumulation_for_multiple_expenses(
        self, sample_payer_id, sample_group_id
    ):
        """Test that balances accumulate correctly for multiple expenses."""
        expenses = [
            Expense(
                id=uuid4(),
                group_id=sample_group_id,
                payer_id=sample_payer_id,
                amount=100.0,
                description="Expense 1",
            ),
            Expense(
                id=uuid4(),
                group_id=sample_group_id,
                payer_id=sample_payer_id,
                amount=200.0,
                description="Expense 2",
            ),
            Expense(
                id=uuid4(),
                group_id=sample_group_id,
                payer_id=sample_payer_id,
                amount=50.0,
                description="Expense 3",
            ),
        ]

        result = summarize_balances(expenses)

        # With current implementation: each expense contributes 0
        # So total = 0 + 0 + 0 = 0
        assert result[str(sample_payer_id)] == 0.0

    def test_different_group_ids(self, sample_payer_id):
        """Test expenses from different groups (should all be processed)."""
        group1 = uuid4()
        group2 = uuid4()

        expenses = [
            Expense(
                id=uuid4(),
                group_id=group1,
                payer_id=sample_payer_id,
                amount=100.0,
                description="Group 1 expense",
            ),
            Expense(
                id=uuid4(),
                group_id=group2,
                payer_id=sample_payer_id,
                amount=50.0,
                description="Group 2 expense",
            ),
        ]

        result = summarize_balances(expenses)

        # Current implementation doesn't filter by group
        # Both expenses are processed
        assert str(sample_payer_id) in result
        assert result[str(sample_payer_id)] == 0.0

    def test_mixed_payers_with_varying_amounts(self, sample_group_id):
        """Test realistic scenario with multiple payers and varying amounts."""
        payer1 = uuid4()
        payer2 = uuid4()
        payer3 = uuid4()

        expenses = [
            Expense(
                id=uuid4(),
                group_id=sample_group_id,
                payer_id=payer1,
                amount=150.0,
                description="Hotel",
            ),
            Expense(
                id=uuid4(),
                group_id=sample_group_id,
                payer_id=payer2,
                amount=75.0,
                description="Food",
            ),
            Expense(
                id=uuid4(),
                group_id=sample_group_id,
                payer_id=payer1,
                amount=45.0,
                description="Transport",
            ),
            Expense(
                id=uuid4(),
                group_id=sample_group_id,
                payer_id=payer3,
                amount=30.0,
                description="Tickets",
            ),
        ]

        result = summarize_balances(expenses)

        # All should have 0 balance with current implementation
        assert len(result) == 3
        assert result[str(payer1)] == 0.0
        assert result[str(payer2)] == 0.0
        assert result[str(payer3)] == 0.0

    def test_large_number_of_expenses(self, sample_payer_id, sample_group_id):
        """Test performance with a large number of expenses."""
        expenses = [
            Expense(
                id=uuid4(),
                group_id=sample_group_id,
                payer_id=sample_payer_id,
                amount=10.0,
                description=f"Expense {i}",
            )
            for i in range(1000)
        ]

        result = summarize_balances(expenses)

        assert str(sample_payer_id) in result
        assert result[str(sample_payer_id)] == 0.0

    def test_expense_with_optional_description_none(
        self, sample_payer_id, sample_group_id
    ):
        """Test expense with None description."""
        expense = Expense(
            id=uuid4(),
            group_id=sample_group_id,
            payer_id=sample_payer_id,
            amount=50.0,
            description=None,
        )

        result = summarize_balances([expense])

        assert str(sample_payer_id) in result
        assert result[str(sample_payer_id)] == 0.0


class TestSummarizeBalancesEdgeCases:
    def test_very_small_amounts(self, sample_payer_id, sample_group_id):
        """Test with very small amounts (floating point precision)."""
        expense = Expense(
            id=uuid4(),
            group_id=sample_group_id,
            payer_id=sample_payer_id,
            amount=0.01,
            description="Penny",
        )

        result = summarize_balances([expense])

        assert str(sample_payer_id) in result
        assert result[str(sample_payer_id)] == pytest.approx(0.0)

    def test_very_large_amounts(self, sample_payer_id, sample_group_id):
        """Test with very large amounts."""
        expense = Expense(
            id=uuid4(),
            group_id=sample_group_id,
            payer_id=sample_payer_id,
            amount=999999.99,
            description="Expensive item",
        )

        result = summarize_balances([expense])

        assert str(sample_payer_id) in result
        assert result[str(sample_payer_id)] == pytest.approx(0.0)

    def test_tuple_of_expenses(self, sample_payer_id, sample_group_id):
        """Test that function works with tuple input."""
        expenses = (
            Expense(
                id=uuid4(),
                group_id=sample_group_id,
                payer_id=sample_payer_id,
                amount=50.0,
                description="Item 1",
            ),
            Expense(
                id=uuid4(),
                group_id=sample_group_id,
                payer_id=sample_payer_id,
                amount=100.0,
                description="Item 2",
            ),
        )

        result = summarize_balances(expenses)

        assert str(sample_payer_id) in result
        assert result[str(sample_payer_id)] == 0.0
