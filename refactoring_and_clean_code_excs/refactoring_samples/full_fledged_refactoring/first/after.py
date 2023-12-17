class BaseCreateCustomerRequest(BaseModel, extra=Extra.forbid):
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
    customer_id: str | None = Field(
        default=None,
        description="An identification number of the legal customer",
        min_length=1,
        max_length=30,
    )


class IndividualCustomerRequest(BaseCreateCustomerRequest):
    individual_info: IndividualSchemaRequest | None = Field(
        default=None,
        description="A set of metadata describing the individual",
    )


class OrganizationCustomerRequest(BaseCreateCustomerRequest):
    organization_info: OrganizationSchemaRequest | None = Field(
        default=None,
        description="A set of metadata describing the organization",
    )
