class CreateCustomerRequest(BaseModel, extra=Extra.forbid):
    """A schema for a request to create a customer of different types"""

    location_info: AddressSchema = Field(
        description="An address description of the customer",
    )
    contact_email: EmailStr = Field(description="An official email address of the customer")
    contact_phone: str | None = Field(
        default=None,
        description="A phone number of the customer",
        min_length=1,
        max_length=100,
    )
    customer_website: HttpUrl | None = Field(default=None, description="A website of the customer")
    organization_info: OrganizationSchemaRequest | None = Field(
        default=None,
        description="A set of metadata describing the organization",
    )
    individual_info: IndividualSchemaRequest | None = Field(
        default=None,
        description="A set of metadata describing the individual",
    )
    customer_id: str | None = Field(
        default=None,
        description="An identification number of the legal customer",
        min_length=1,
        max_length=30,
    )
    customer_type: TypeEnum = Field(..., description="A type for a customer")

    @root_validator(pre=True)
    def check_type(cls, fields: dict[Any, Any]):  # noqa: N805
        type_ = fields.get("customer_type")
        if not fields.get(type_):
            raise ValueError(f"Value of `{type_}` key cannot be null")  # pragma: no cover
        return fields


class UpdateCustomerRequest(BaseModel, extra=Extra.forbid):
    """A schema for a request to update a customer"""

    location_info: AddressSchema | None = Field(
        default=None,
        description="An address description of the customer",
    )

    contact_email: EmailStr | None = Field(
        default=None,
        description="An official email address of the customer",
    )
    contact_phone: str | None = Field(
        default=None,
        description="A phone number of the customer",
        min_length=1,
        max_length=100,
    )
    customer_website: HttpUrl | None = Field(default=None, description="A website of the customer")
    customer_id: str | None = Field(
        default=None,
        description="An identification number of the legal customer",
        max_length=30,
    )
    org_info: OptionalOrganizationSchema | None = Field(
        description="A set of metadata describing the organization",
    )
    individual_info: OptionalIndividualSchema | None = Field(
        default=None,
        description="A set of metadata describing the individual",
    )

    @root_validator(pre=True)
    def check_type(cls, fields: dict[str, Any]):  # noqa: N805
        if fields.get("org_info") and fields.get("individual_info"):
            raise ValueError(  # pragma: no cover
                "Only 1 key from `org_info` and `individual_info` should be provided",
            )
        return fields

