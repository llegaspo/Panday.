import uuid
from django.db import models
from django.conf import settings
from django.db.models import Sum


class Wallet(models.Model):
    wallet_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="wallet"
    )
    balance = models.DecimalField(max_digits=14, decimal_places=2, default=0.00)
    escrow_balance = models.DecimalField(max_digits=14, decimal_places=2, default=0.00)
    withdrawable_balance = models.DecimalField(
        max_digits=14, decimal_places=2, default=0.00
    )
    frozen_balance = models.DecimalField(max_digits=14, decimal_places=2, default=0.00)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "WALLETS"
        verbose_name = "Wallet"

    def __str__(self):
        return f"Wallet for {self.user} (${self.balance})"

    def recalculate_total(self):
        self.balance = (
            self.escrow_balance + self.withdrawable_balance + self.frozen_balance
        )
        self.save()


class Transaction(models.Model):
    class Type(models.TextChoices):
        ESCROW_DEPOSIT = "ESCROW_DEPOSIT", "Escrow Deposit"
        RELEASE = "RELEASE", "Release Funds"
        FEE = "FEE", "Platform Fee"
        REFUND = "REFUND", "Refund"
        WITHDRAWAL = "WITHDRAWAL", "Withdrawal"
        TOP_UP = "TOP_UP", "Top Up"

    transaction_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )

    source_wallet = models.ForeignKey(
        Wallet,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="outgoing_transactions",
    )

    dest_wallet = models.ForeignKey(
        Wallet,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="incoming_transactions",
    )

    booking = models.ForeignKey(
        "Booking",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transactions",
    )

    amount = models.DecimalField(max_digits=14, decimal_places=2)
    transaction_type = models.CharField(max_length=30, choices=Type.choices)

    platform_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "TRANSACTIONS"
        verbose_name = "Transaction"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["transaction_type"]),
            models.Index(fields=["source_wallet"]),
            models.Index(fields=["dest_wallet"]),
        ]

    def __str__(self):
        return f"{self.transaction_type}: {self.amount}"
